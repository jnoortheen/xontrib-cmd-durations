import builtins
import subprocess
from notifypy import Notify
from loguru import logger

xsh = builtins.__xonsh__
LONG_DURATION = xsh.env.get("LONG_DURATION", 5)  # seconds


def secs_to_readable(secs: int):
    """

    Parameters
    ----------
    secs

    >>> secs_to_readable(100)
    '1m40s'
    """
    secs = round(secs)
    readable = ""
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        readable += str(hours) + "h"
    if hours or minutes:
        readable += str(minutes) + "m"
    if hours or minutes or seconds:
        readable += str(seconds) + "s"
    return readable


def get_current_window_id() -> str:
    return subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()


def notify_user(hist, readable: str):
    winid = xsh.env.get("WINDOWID")
    curr_winid = get_current_window_id()
    if curr_winid != winid:
        rtn = hist.rtns[-1]
        cmd = hist.inps[-1]

        noti = Notify()
        noti.title = str(f"xonsh {cmd}")
        noti.message = f'{"Failed" if rtn else "Done"} in {readable}'
        noti.send()


def long_cmd_duration():
    history = xsh.history
    if not history.tss:
        return

    start_t, end_t = history.tss[-1]
    interval = end_t - start_t

    if interval > LONG_DURATION:
        readable = secs_to_readable(interval)
        try:
            notify_user(history, readable)
        except Exception as ex:
            logger.warning(f"Failed to send notification {ex}")

        return readable
    return None


xsh.env["PROMPT_FIELDS"]["long_cmd_duration"] = long_cmd_duration
