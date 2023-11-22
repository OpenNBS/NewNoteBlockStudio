import sys

if __name__ == "__main__":
    if "--player" in sys.argv:
        from nbs.app_playermode import AppContext

        print("Running in player mode")
    else:
        from nbs.app import AppContext

        print("Running in editor mode")

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
