"""
Integration tests for the ttc worker process (JSON protocol over stdio).
"""

import json
import os
import subprocess
import sys
import threading
import time

import pytest

pytestmark = pytest.mark.integration

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class WorkerClient:
    """Test client that speaks the newline-delimited JSON worker protocol."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            ROOT + os.pathsep + existing if existing else ROOT
        )
        self.proc = subprocess.Popen(
            [sys.executable, "-u", "-m", "ttc.worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
            cwd=ROOT,
        )

    def send(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def _read_line(self) -> str:
        box = []

        def reader():
            box.append(self.proc.stdout.readline())

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        thread.join(self.timeout)
        if not box:
            raise AssertionError(
                f"worker did not respond within {self.timeout}s"
            )
        return box[0]

    def read_message(self) -> dict:
        line = self._read_line()
        assert line != "", (
            "worker closed stdout unexpectedly; stderr:\n"
            + self.proc.stderr.read()
        )
        return json.loads(line)

    def request(self, message: dict) -> dict:
        """Send a request and read replies until the matching id arrives.

        input_request messages are answered with answers[id] when provided.
        """
        answers = message.pop("_answers", {})
        self.send(message)
        request_id = message.get("id")
        while True:
            reply = self.read_message()
            if reply.get("cmd") == "input_request":
                key = str(reply.get("prompt", ""))
                answer = answers.get(key, answers.get("*", ""))
                self.send({"cmd": "input_answer", "answer": answer})
                continue
            if reply.get("id") == request_id or request_id is None:
                return reply

    def close(self, expect_exit_code: int = 0) -> int:
        try:
            if self.proc.poll() is None:
                self.proc.stdin.close()
                self.proc.wait(timeout=self.timeout)
        finally:
            if self.proc.poll() is None:
                self.proc.kill()
                self.proc.wait(timeout=10)
        if expect_exit_code is not None:
            assert self.proc.returncode == expect_exit_code
        return self.proc.returncode

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if exc_info[0] is not None:
            if self.proc.poll() is None:
                self.proc.kill()
                self.proc.wait(timeout=10)
            return False
        self.close()
        return False


@pytest.fixture
def client():
    with WorkerClient() as worker:
        yield worker


class TestWorkerProtocol:
    def test_ping(self, client):
        reply = client.request({"id": 1, "cmd": "ping"})
        assert reply["ok"] is True
        assert reply["result"] == "pong"
        assert reply["version"]

    def test_translate_assignment(self, client):
        reply = client.request({"id": 2, "cmd": "translate", "text": "set x to 5"})
        assert reply["ok"] is True
        result = reply["result"]
        assert result["success"] is True
        assert "x = 5" in result["python_code"]

    def test_translate_invalid_text(self, client):
        reply = client.request(
            {"id": 3, "cmd": "translate", "text": "zzz qqq no pattern here"}
        )
        assert reply["ok"] is True
        assert reply["result"]["success"] is False
        assert reply["result"]["error_message"].strip()

    def test_translate_missing_text(self, client):
        reply = client.request({"id": 4, "cmd": "translate"})
        assert reply["ok"] is False
        assert "text" in reply["error"]

    def test_execute_success(self, client):
        reply = client.request(
            {"id": 5, "cmd": "execute", "code": "print('hello from worker')"}
        )
        assert reply["ok"] is True
        result = reply["result"]
        assert result["success"] is True
        assert "hello from worker" in result["stdout"]
        assert result["execution_time"] >= 0

    def test_execute_runtime_error(self, client):
        reply = client.request(
            {"id": 6, "cmd": "execute", "code": "result = 1 / 0"}
        )
        assert reply["ok"] is True
        result = reply["result"]
        assert result["success"] is False
        assert "ZeroDivisionError" in result["error_message"]

    def test_execute_syntax_error_is_caught_locally(self, client):
        reply = client.request(
            {"id": 7, "cmd": "execute", "code": "print('unterminated"}
        )
        assert reply["ok"] is True
        result = reply["result"]
        assert result["success"] is False
        assert "syntax" in result["error_message"].lower()

    def test_execute_with_interactive_input(self, client):
        reply = client.request({
            "id": 8,
            "cmd": "execute",
            "code": "name = input('name? ')\nprint('hi ' + name)",
            "_answers": {"name? ": "Budi"},
        })
        assert reply["ok"] is True
        result = reply["result"]
        assert result["success"] is True, result.get("error_message")
        assert "hi Budi" in result["stdout"]

    def test_execute_timeout(self, client):
        start = time.time()
        reply = client.request({
            "id": 9,
            "cmd": "execute",
            "code": "while True:\n    pass",
            "timeout": 1.0,
        })
        elapsed = time.time() - start
        assert reply["ok"] is True
        assert reply["result"]["success"] is False
        assert "timeout" in reply["result"]["error_message"].lower()
        assert elapsed < 10.0

    def test_unknown_command(self, client):
        reply = client.request({"id": 10, "cmd": "explode"})
        assert reply["ok"] is False
        assert "explode" in reply["error"]

    def test_malformed_json_keeps_worker_alive(self, client):
        client.proc.stdin.write("this is not json\n")
        client.proc.stdin.flush()
        reply = client.read_message()
        assert reply["ok"] is False
        assert reply["id"] is None
        # worker still serves after a protocol violation
        pong = client.request({"id": 11, "cmd": "ping"})
        assert pong["ok"] is True

    def test_multiple_requests_same_session(self, client):
        for i in range(3):
            reply = client.request(
                {"id": 100 + i, "cmd": "translate", "text": f"set v{i} to {i}"}
            )
            assert reply["ok"] is True
            assert f"v{i} = {i}" in reply["result"]["python_code"]

    def test_stdout_is_pure_json_stream(self, client):
        reply = client.request({"id": 12, "cmd": "ping"})
        assert reply["ok"] is True
        # Any log line on stdout would have crashed json.loads in read_message;
        # additionally ensure stderr may carry logs without breaking the stream.
        assert client.proc.stderr is not None

    def test_shutdown_exits_cleanly(self):
        with WorkerClient() as client:
            reply = client.request({"id": 13, "cmd": "shutdown"})
            assert reply["ok"] is True
            code = client.proc.wait(timeout=30)
            assert code == 0
