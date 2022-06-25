import pstats

with open("profile2.txt", "w") as stream:
    p = pstats.Stats("profile.txt", stream=stream)
    p.strip_dirs().sort_stats("cumtime").print_stats()
