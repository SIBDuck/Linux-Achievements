# Linux Achievements
## What is this??
It is a fully free (open source) utility, adding achievements into your GNU/Linux system and licensed under [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html) ([what is AGPLv3](https://www.gnu.org/licenses/why-affero-gpl.html))! Your latest terminal command is logged and parsed in real time, to determine whether you unlock a new achievement.
## Is it safe?
Yes, it is absolutely safe. Your last command is written directly to `XDG_RUNTIME_DIR` (usually `/run/user/$(id -u)`). This directory is mounted as a tmpfs RAM drive, ensuring that only YOUR specific user has access to it. Your data is strictly local, requires no internet connection, and cannot be stolen!