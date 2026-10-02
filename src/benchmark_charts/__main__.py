from .cli import main as cli_main


def main():
    import sys

    raise SystemExit(cli_main(sys.argv[1:]))


if __name__ == "__main__":
    main()
