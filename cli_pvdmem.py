# Small CLI utility for main module debugging

import sys
from pvdmem import parse_raw_dump, make_clear_parsels, create_pcap
from pprint import pprint


def read_file_content(path: str, encoding: str = "utf-8") -> str:
    """Reads the content of a file and returns it as a string."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli_pvdmem.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    try:
        raw_dump = read_file_content(filename)
        parsed_dump = parse_raw_dump(raw_dump.split('Wallclock: '))
        cleared_parcels = make_clear_parsels(parsed_dump)
        print(parsed_dump)

    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
    except Exception as e:
        print(f"Error while reading the file: {e}")

if __name__ == "__main__":
    main()