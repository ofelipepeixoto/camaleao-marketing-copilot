"""CLI: python -m camaleao_marketing input.json --output NEW-report.json."""

import argparse
import sys

from .core import InputError, analyze, load_input, write_report


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "Invalid command. Use --help for the offline CLI syntax.\n")


def main(argv=None):
    parser = _Parser(description="Offline observations from a local JSON file; human review required.")
    parser.add_argument("input", help="Existing local UTF-8 JSON file (at most 1 MiB).")
    parser.add_argument("--output", required=True, help="New local report; existing files are refused.")
    args = parser.parse_args(argv)
    try:
        write_report(args.output, analyze(load_input(args.input)))
    except (InputError, OSError, UnicodeError, ValueError, RecursionError):
        print("Input or output could not be processed safely.", file=sys.stderr)
        return 2
    print("Offline report created. Human review remains pending; execution is not authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
