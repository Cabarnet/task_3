import os
import platform
import shlex
import subprocess
import sys

def in_pty() -> bool:
    """
    Возвращает True, если текущий процесс запущен в «настоящем» терминале
    (есть псевдотерминал / интерактивный stdin).
    """
    try:
        return sys.stdin.isatty()
    except Exception:
        return False

def run_external():
    """
    Открывает новое окно терминала и запускает модуль с curses-меню:
    `python -m ui.main_windows`.
    """
    cmd = [sys.executable, "-m", "ui.main_windows"]

    if os.name == "nt":
        # Windows: новое окно консоли
        CREATE_NEW_CONSOLE = 0x00000010
        subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE, cwd=os.getcwd())
    else:
        # *nix/macOS
        term_cmds = [
            ["x-terminal-emulator", "-e"] + cmd,
            ["gnome-terminal", "--"] + cmd,
            ["konsole", "-e"] + cmd,
            ["xfce4-terminal", "-e", " ".join(shlex.quote(c) for c in cmd)],
        ]
        for tcmd in term_cmds:
            try:
                subprocess.Popen(tcmd, cwd=os.getcwd())
                break
            except FileNotFoundError:
                continue
        else:
            if platform.system() == "Darwin":
                # macOS через AppleScript
                quoted = " ".join(shlex.quote(c) for c in cmd)
                osa = f'tell application "Terminal" to do script "cd {shlex.quote(os.getcwd())}; {quoted}"'
                subprocess.Popen(["osascript", "-e", osa])
            else:
                # Фоллбек: запускаем в текущем окне
                subprocess.Popen(cmd, cwd=os.getcwd())

if __name__ == "__main__":
    """
    Запуск:
    - Если текущий процесс — настоящий терминал, запускаем curses напрямую.
    - Иначе — открываем новое окно терминала.
    """
    if in_pty():
        try:
            import curses
            from ui.main_windows import main  # main(stdscr)
            curses.wrapper(main)
        except Exception as e:
            print("Ошибка запуска интерфейса:", e)
    else:
        run_external()
