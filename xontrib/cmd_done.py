import functools
import subprocess as sp

from xonsh.built_ins import XSH

xsh = XSH
LONG_DURATION = xsh.env.get("XONRTIB_CD_LONG_DURATION", 5)  # seconds
TRIGGER_NOTIFICATION = xsh.env.get("XONRTIB_CD_TRIGGER_NOTIFICATION", True)


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


def is_system(system: str):
    import platform

    return platform.system() == system


@functools.lru_cache(None)
def is_linux_system():
    return is_system("Linux")


@functools.lru_cache(None)
def is_darwin_system():
    return is_system("Darwin")


def _xdotool_window_id():
    try:
        return sp.check_output(["xdotool", "getactivewindow"]).decode().strip()
    except Exception as ex:
        import logging

        logging.warning(
            f"Failed to send notification {ex}. Make sure that xdotool is installed."
        )


def _linux_is_app_window_focused():
    winid = xsh.env.get("WINDOWID")
    if not winid:
        import logging

        logging.warning(
            "Environment variable $WINDOWID is unset. It should be set by the terminal application on shell startup. "
            "Not able to find active window."
        )
        return False
    curr_winid = _xdotool_window_id()
    return curr_winid == winid


def _darwin_is_app_window_focused():
    term = xsh.env.get("TERM_PROGRAM")
    if not term:
        import logging

        logging.warning(
            "Environment variable $TERM_PROGRAM is unset. "
            "It should be set by the terminal application on shell startup. "
            "Not able to find active window."
        )
        return False

    term = str(term).rstrip(".app")
    out = sp.check_output(["lsappinfo", "info", "-app", term])
    return b"(in front)" in out


def is_app_window_focused():
    # https://stackoverflow.com/questions/10266281/obtain-active-window-using-python
    if is_darwin_system():
        return _darwin_is_app_window_focused()

    if is_linux_system():
        return _linux_is_app_window_focused()
    return False


def notify_user(hist, readable: str):
    rtn = hist.rtns[-1]
    cmd = hist.inps[-1]

    if is_app_window_focused():
        return

    from notifypy import Notify

    noti = Notify()
    noti.title = str(f"{cmd}")
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
        if TRIGGER_NOTIFICATION:
            notify_user(history, readable)
        return readable
    return None


xsh.env["PROMPT_FIELDS"]["long_cmd_duration"] = long_cmd_duration
