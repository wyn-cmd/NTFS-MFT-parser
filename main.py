# entry point for the ntfs mft parser tool
# builds and displays the timeline from the test log

import sys
from timeline import build_timeline, print_timeline

# main routine to orchestrate timeline generation and output
def main():
    try:
        timeline = build_timeline("test.log", limit=500)
    except FileNotFoundError:
        print("error: test.log not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error building timeline: {e}", file=sys.stderr)
        sys.exit(1)

    print_timeline(timeline)

if __name__ == "__main__":
    main()