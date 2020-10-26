<p align="center">
Send notification once long running command is finished. Add duration PROMP_FIELD.
</p>

<p align="center">
If you like the idea click ⭐ on the repo and stay tuned.
</p>

## Installation

To install use pip:

``` bash
xpip install xontrib-cmd-durations
# or: xpip install -U git+https://github.com/jnoortheen/xontrib-cmd-durations
```

## Usage

``` bash
xontrib load cmd_done
```

## Usage

* makes `long_cmd_duration` available to the `$PROMP_FIELD `
* if the command is taking more than `$LONG_DURATION` seconds
  + it is `long_cmd_duration` returns the duration in human readable way
  + a desktop notification is sent if the terminal is not focused.
    - **Note**: Currently the focusing part requires `xdotool` to be installed.

        So the notification part will not work in Windows/OSX. PRs welcome on that.

``` bash
$RIGHT_PROMPT = '{long_cmd_duration:⌛{}}{user:{{BOLD_RED}}🤖{}}{hostname:{{BOLD_#FA8072}}🖥{}}'
```

![](./images/2020-10-26-10-59-38.png)

## Credits

This package was created with [xontrib cookiecutter template](https://github.com/jnoortheen/xontrib-cookiecutter).
