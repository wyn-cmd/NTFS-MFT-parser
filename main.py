# entry point for the ntfs mft parser tool
# builds and displays the timeline from the test log

from timeline import build_timeline, print_timeline

def main():
    # load and parse the timeline entries up to the default limit
    try:
        timeline = build_timeline("MFT.raw", limit=500)
    except FileNotFoundError:
        print("error: MFT.raw not found. Extract the $MFT from an NTFS volume "
              "and place it in the project directory as MFT.raw.")
        return
    except Exception as e:
        print(f"error building timeline: {e}")
        return

    # output the results to stdout
    print_timeline(timeline)

if __name__ == "__main__":
    main()