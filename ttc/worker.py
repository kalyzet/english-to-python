"""
Worker process: newline-delimited JSON bridge between the GUI and the engine.

Protocol (stdin):  one JSON object per line
    {"id": 1, "cmd": "translate", "text": "set x to 5"}
    {"id": 2, "cmd": "execute", "code": "print(1)", "timeout": 5.0,
     "allow_imports": false}
    {"id": 3, "cmd": "ping"}
    {"id": 4, "cmd": "shutdown"}
    {"cmd": "input_answer", "answer": "user reply"}   (reply to input_request)

Protocol (stdout): one JSON object per line
    {"id": 1, "ok": true, "result": {<TranslationResult.to_dict()>}}
    {"id": 2, "ok": true, "result": {<ExecutionResult.to_dict()>}}
    {"id": 3, "ok": true, "result": "pong", "version": "0.2.0"}
    {"ok": false, "error": "..."}                     (id null when unknown)
    {"id": 2, "cmd": "input_request", "prompt": "..."} (worker -> GUI, during
      an "execute" whose code calls input())

Logging goes to stderr only; stdout is reserved for the JSON stream.
"""

import json
import logging
import sys
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple

from . import __version__
from .engine.translator import TranslationEngine
from .sandbox import CodeExecutionService, ExecutionConfig

logger = logging.getLogger("ttc.worker")


class Worker:
    """Serves JSON commands read line-by-line from stdin."""

    def __init__(
        self,
        stdin: Optional[TextIO] = None,
        stdout: Optional[TextIO] = None,
    ) -> None:
        self.stdin: TextIO = stdin if stdin is not None else sys.stdin
        self.stdout: TextIO = stdout if stdout is not None else sys.stdout
        self.engine = TranslationEngine()
        self._pending_lines: List[str] = []

    # ------------------------------------------------------------------ I/O
    def _send(self, message: Dict[str, Any]) -> None:
        self.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.stdout.flush()

    def _readline(self) -> Optional[str]:
        if self._pending_lines:
            return self._pending_lines.pop(0)
        line = self.stdin.readline()
        if line == "":
            return None
        return line

    # ------------------------------------------------------------- commands
    def _handle_translate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        text = request.get("text")
        if not isinstance(text, str):
            raise ValueError("'text' must be a string")
        result = self.engine.translate(text)
        return {"id": request.get("id"), "ok": True, "result": result.to_dict()}

    def _handle_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        code = request.get("code")
        if not isinstance(code, str):
            raise ValueError("'code' must be a string")

        config = ExecutionConfig()
        timeout = request.get("timeout")
        if isinstance(timeout, (int, float)) and timeout > 0:
            config.timeout_seconds = float(timeout)
        allow_imports = request.get("allow_imports")
        if isinstance(allow_imports, bool):
            config.allow_imports = allow_imports

        service = CodeExecutionService(config)
        handler = self._make_input_handler(request.get("id"))
        result = service.execute_code(code, user_input_handler=handler)
        return {"id": request.get("id"), "ok": True, "result": result.to_dict()}

    def _make_input_handler(self, request_id: Any) -> Callable[[str], str]:
        """Ask the GUI for input() answers while an execute request is running.

        The main loop is blocked inside execute_code(), so reading stdin here
        does not race with it; unrelated lines are queued for later.
        """

        def handler(prompt: str) -> str:
            self._send({
                "id": request_id,
                "cmd": "input_request",
                "prompt": str(prompt),
            })
            while True:
                line = self.stdin.readline()
                if line == "":
                    raise RuntimeError("GUI closed the connection during input()")
                line = line.strip()
                if not line:
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(message, dict) and message.get("cmd") == "input_answer":
                    return str(message.get("answer", ""))
                self._pending_lines.append(
                    json.dumps(message, ensure_ascii=False)
                )

        return handler

    def _handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": request.get("id"),
            "ok": True,
            "result": "pong",
            "version": __version__,
        }

    def _handle_shutdown(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": request.get("id"), "ok": True, "result": "bye"}

    # ------------------------------------------------------------------ loop
    def dispatch(self, request: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Handle one request; returns (response, keep_running)."""
        cmd: Any = request.get("cmd")
        handlers = {
            "translate": self._handle_translate,
            "execute": self._handle_execute,
            "ping": self._handle_ping,
            "shutdown": self._handle_shutdown,
        }
        handler = handlers.get(cmd)
        if handler is None:
            return {
                "id": request.get("id"),
                "ok": False,
                "error": f"unknown command: {cmd!r}",
            }, True
        try:
            response = handler(request)
        except Exception as exc:  # noqa: BLE001 - report to GUI, keep serving
            logger.exception("command %r failed", cmd)
            return {
                "id": request.get("id"),
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }, True
        return response, cmd != "shutdown"

    def run(self) -> int:
        logger.info("worker started (version %s)", __version__)
        while True:
            line = self._readline()
            if line is None:
                logger.info("stdin closed, exiting")
                return 0
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                if not isinstance(request, dict):
                    raise ValueError("request must be a JSON object")
            except (json.JSONDecodeError, ValueError) as exc:
                self._send({"id": None, "ok": False, "error": f"invalid request: {exc}"})
                continue
            response, keep_running = self.dispatch(request)
            self._send(response)
            if not keep_running:
                logger.info("shutdown requested")
                return 0


def main() -> int:
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    return Worker().run()


if __name__ == "__main__":
    sys.exit(main())
