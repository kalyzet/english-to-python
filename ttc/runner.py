"""
Child process that executes user code in isolation.

Run as:  python -m ttc.runner
Protocol (stdin):  first line = JSON payload, then one line per input() answer.
Protocol (stdout): user output; input() requests are sent as sentinel lines
                   "@@__TTC_INPUT__@@" + json-encoded prompt.
Protocol (stderr): traceback on failure; process exit code 0 = success.
"""

import json
import sys
import traceback
from typing import Any, Callable, Dict

INPUT_SENTINEL = "@@__TTC_INPUT__@@"


def build_safe_builtins(allow_imports: bool) -> Dict[str, Any]:
    """Restricted builtin set for user code (mirrors the documented safe list)."""
    import builtins as B

    names = [
        'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
        'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
        'getattr', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
        'issubclass', 'iter', 'len', 'list', 'map', 'max', 'min',
        'next', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
        'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
        'str', 'sum', 'tuple', 'type', 'zip',
    ]
    safe = {name: getattr(B, name) for name in names if hasattr(B, name)}
    if allow_imports:
        safe['__import__'] = B.__import__
    return safe


def make_input() -> Callable[..., str]:
    """input() replacement that talks to the parent process."""

    def safe_input(prompt: str = '') -> str:
        sys.stdout.write(INPUT_SENTINEL + json.dumps(str(prompt)))
        sys.stdout.write('\n')
        sys.stdout.flush()
        line = sys.stdin.readline()
        if line == '':
            raise EOFError("No input available from parent process")
        if line.endswith('\n'):
            line = line[:-1]
        if line.endswith('\r'):
            line = line[:-1]
        return line

    return safe_input


def main() -> int:
    payload_line = sys.stdin.readline()
    if not payload_line:
        print("runner: no payload received", file=sys.stderr)
        return 2

    try:
        payload = json.loads(payload_line)
    except json.JSONDecodeError as exc:
        print(f"runner: bad payload: {exc}", file=sys.stderr)
        return 2

    code = payload.get('code', '')
    allow_imports = bool(payload.get('allow_imports', True))
    interactive = bool(payload.get('interactive', False))

    safe_builtins = build_safe_builtins(allow_imports)
    if interactive:
        safe_builtins['input'] = make_input()

    exec_globals = {'__builtins__': safe_builtins, '__name__': '__main__'}

    try:
        compiled = compile(code, '<string>', 'exec')
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        return 1

    try:
        exec(compiled, exec_globals)
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
