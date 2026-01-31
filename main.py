from timeline import build_timeline, print_timeline

timeline = build_timeline("test.log", limit=500)
print_timeline(timeline)
