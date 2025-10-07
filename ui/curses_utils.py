import curses

def cinput(stdscr, y: int, x: int, prompt_text: str, max_length: int = 50) -> str:
    """
    Ввод текста пользователем в curses.
    
    Параметры:
    - stdscr: главное окно curses
    - y, x: координаты начала строки
    - prompt_text: текст запроса
    - max_length: максимальная длина вводимой строки
    """
    stdscr.addstr(y, x, prompt_text)
    stdscr.refresh()
    curses.echo()  # показываем вводимые символы
    input_bytes = stdscr.getstr(y, x + len(prompt_text), max_length)
    curses.noecho()
    return input_bytes.decode("utf-8")

def cprint(stdscr, text: str, wait_for_key: bool = False):
    """
    Показывает многострочное сообщение по центру экрана.

    Параметры:
    - stdscr: curses окно
    - text: текст сообщения (можно с переносами '\n')
    - wait_for_key: если True, ждём нажатия клавиши после отображения всего текста
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    lines = text.split('\n')
    start_y = max(0, (h - len(lines)) // 2)

    for i, line in enumerate(lines):
        x = max(0, (w - len(line)) // 2)
        # Добавляем строку по центру
        stdscr.addstr(start_y + i, x, line)

    stdscr.refresh()

    if wait_for_key:
        stdscr.getch()  # ждём только один раз после вывода всего текста