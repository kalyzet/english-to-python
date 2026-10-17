"""CLI entry point: python -m ttc "your english sentence"."""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .engine.translator import TranslationEngine


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m ttc",
        description="Translate English sentences into Python code.",
    )
    parser.add_argument("text", nargs="*", help="English sentence(s) to translate")
    parser.add_argument("--run", action="store_true", help="Execute the generated code")
    parser.add_argument("--version", action="version", version=f"ttc {__version__}")
    args = parser.parse_args(argv)

    text = " ".join(args.text).strip()
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        if not text:
            parser.print_help()
            return 2

    engine = TranslationEngine()
    result = engine.translate(text)

    if not result.success:
        print(f"ERROR: {result.error_message}", file=sys.stderr)
        return 1

    print(result.python_code)

    if args.run:
        from .sandbox import CodeExecutionService

        execution = CodeExecutionService().execute_code(result.python_code)
        if execution.stdout:
            print(execution.stdout, end="")
        if not execution.success:
            print(execution.error_message or execution.stderr, file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
