KEY_LABELS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def ticks_to_seconds(ticks: float, tempo: float) -> float:
    return ticks / tempo


def seconds_to_ticks(seconds: float, tempo: float) -> float:
    return seconds * tempo


def timestr(minutes: int, seconds: int, ms: int) -> str:
    return f"{minutes:02d}:{seconds:02d},{ms:03d}"


def seconds_to_timestr(seconds: float) -> str:
    seconds, ms = divmod(int(seconds * 1000), 1000)
    minutes, seconds = divmod(seconds, 60)
    return timestr(minutes, seconds, ms)


def ticks_to_timestr(ticks: int, tempo: float) -> str:
    seconds = ticks_to_seconds(ticks, tempo)
    return seconds_to_timestr(seconds)
