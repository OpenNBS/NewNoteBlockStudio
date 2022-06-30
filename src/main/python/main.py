import sys

from nbs.app import AppContext

if __name__ == "__main__":

    if "--profile" in sys.argv:
        import cProfile
        import datetime
        import os
        import pstats
        from pathlib import Path

        # get current time as a filename
        now = datetime.datetime.now()
        filetime = now.strftime("%Y-%m-%d_%H-%M-%S")

        # run the application
        prof_path = Path(".tmp")
        prof_file = prof_path / f"profile_{filetime}.prof"
        cProfile.run("AppContext().run()", prof_file)

        # create a pstats object from the profile file
        pstats_file = prof_path / f"profile_{filetime}.txt"
        with open(pstats_file, "w") as stream:
            p = pstats.Stats(str(prof_file), stream=stream)
            p.strip_dirs().sort_stats("cumtime").print_stats()

        # open the profiler file in snakeviz
        os.system(f"snakeviz {prof_file}")
        sys.exit(0)

    else:
        appctxt = AppContext()
        exit_code = appctxt.run()
        sys.exit(exit_code)
