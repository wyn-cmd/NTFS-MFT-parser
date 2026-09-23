# entry point for the ntfs mft parser tool
# builds and displays the timeline from the test log

from timeline import build_timeline, print_timeline

def main():
    # load and parse the timeline entries up to the default limit
    try:
        timeline = build_timeline("test.log", limit=500)
    except FileNotFoundError:
        print("error: test.log not found.")
        return
    except Exception as e:
        print(f"error building timeline: {e}")
        return

    # output the results to stdout
    print_timeline(timeline)

if __name__ == "__main__":
    main()