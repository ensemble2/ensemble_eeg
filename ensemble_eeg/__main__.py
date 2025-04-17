import os
import sys

# from .ensemble_eeg import ensemble_edf


def _onerror(e):
    raise e


def do_main(*args: str) -> int:
    """Contains flow control"""
    # process command line arguments
    if len(args) < 2:
        print(f"{args[0]}: missing input directory or file operand", file=sys.stderr)
        return 1
    elif len(args) > 3:
        print(f"{args[0]}: too many arguments", file=sys.stderr)
        return 1

    if os.path.isdir(args[1]):
        # the first argument is a directory containing the files to process
        if len(args) > 2 and not os.path.isdir(args[2]):
            # the second argument must be a directory too
            print(f"{args[0]}: '{args[2]}' is not a directory", file=sys.stderr)
            return 1
        try:
            input_files = [
                os.path.join(root, file)
                for root, dirs, files in os.walk(args[1], onerror=_onerror)
                for file in files
            ]
        except OSError as e:
            print(
                f"{args[0]}: Cannot process '{e.filename}': {e.strerror}",
                file=sys.stderr,
            )
            return 2
    else:
        # the first argument is the file to process
        input_files = [args[1]]

    # pseudonymize each input file and write to outptut directory
    for file in input_files:
        print(file)


def main() -> int:
    """Wrap to main()."""
    try:
        return do_main(*sys.argv)
    except KeyboardInterrupt:
        # User has typed CTRL+C
        sys.stdout.write("\n")
        return 130  # 128 + SIGINT


if __name__ == "__main__":
    sys.exit(main())
