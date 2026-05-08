"""Allow ``python -m cadtestbench`` to invoke the CLI."""
from .cli import main

if __name__ == "__main__":
    _code = main()
    if _code:
        raise SystemExit(_code)
