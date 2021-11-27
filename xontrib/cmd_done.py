import functools
import subprocess as sp

from xonsh.built_ins import XSH
from xonsh.events import events

xsh = XSH
LONG_DURATION = xsh.env.get("LONG_DURATION", 5)  # seconds
CURRENT_WINDOW_ID = []


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


def _lsappinfo_window_id():
    front_app = sp.check_output(["lsappinfo", "front"]).decode()
    out = sp.check_output(
        ["lsappinfo", "info", "-only", "bundleID", front_app]
    ).decode()
    return out.split('"')[-2]


def get_current_window_id() -> str:
    # https://stackoverflow.com/questions/10266281/obtain-active-window-using-python
    if is_linux_system():
        return _xdotool_window_id()
    if is_darwin_system():
        return _lsappinfo_window_id()
    # snippet from https://github.com/franciscolourenco/done/blob/master/conf.d/done.fish
    # elif test -n "$SWAYSOCK"
    #     and type -q jq
    #     swaymsg --type get_tree | jq '.. | objects | select(.focused == true) | .id'
    # else if begin
    #         test "$XDG_SESSION_DESKTOP" = gnome; and type -q gdbus
    #     end
    #     gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval 'global.display.focus_window.get_id()'
    # else if type -q xprop
    #     and test -n "$DISPLAY"
    #     # Test that the X server at $DISPLAY is running
    #     and xprop -grammar >/dev/null 2>&1
    #     xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2
    #     else if uname -a | string match --quiet --ignore-case --regex microsoft
    #         __done_run_powershell_script '
    # Add-Type @"
    #     using System;
    #     using System.Runtime.InteropServices;
    #     public class WindowsCompat {
    #         [DllImport("user32.dll")]
    #         public static extern IntPtr GetForegroundWindow();
    #     }
    # "@
    # [WindowsCompat]::GetForegroundWindow()
    # '


def is_app_window_focused():
    winid = xsh.env.get("WINDOWID")
    curr_winid = get_current_window_id()
    return curr_winid == winid


@events.on_pre_rc
def set_window_id(*_, **__):
    winid = xsh.env.get("WINDOWID")
    if not winid:
        winid = get_current_window_id()
    CURRENT_WINDOW_ID.append(winid)


def notify_user(hist, readable: str):
    rtn = hist.rtns[-1]
    cmd = hist.inps[-1]

    if is_app_window_focused():
        return

    from notifypy import Notify

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
        notify_user(history, readable)
        return readable
    return None


xsh.env["PROMPT_FIELDS"]["long_cmd_duration"] = long_cmd_duration
