import curses
import time
from typing import List, Tuple

Pos = Tuple[int, int]

SYMBOLS = {
    'robot': 'R',
    'free': ' ',
    'wall': '#',
    'path': '*',
}

COLORS = {
    'robot': 1,
    'wall': 2,
    'goal': 3,
    'start': 4,
    'path': 5,
    'weight': 6,
    'text': 7,
}


def _init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLORS['robot'], curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(COLORS['wall'], curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLORS['goal'], curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(COLORS['start'], curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(COLORS['path'], curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(COLORS['weight'], curses.COLOR_YELLOW, -1)
    curses.init_pair(COLORS['text'], curses.COLOR_WHITE, -1)


def _cell_repr(cell: str) -> str:
    if cell in ('#', '1'):
        return SYMBOLS['wall']
    if cell in ('0', 'S', 'E'):
        return cell
    if cell.isdigit():
        return cell
    return cell


def _draw_grid(stdscr, lab: List[List[str]], path: List[Pos], robot_idx: int):
    h, w = stdscr.getmaxyx()
    rows, cols = len(lab), len(lab[0]) if lab else 0

    top = 1
    left = 2

    header = "Curses PathFinder (q = sair, +/- = velocidade)"
    stdscr.attron(curses.color_pair(COLORS['text']))
    stdscr.addstr(0, max(0, (w - len(header)) // 2), header)
    stdscr.attroff(curses.color_pair(COLORS['text']))

    for i in range(rows):
        for j in range(cols):
            ch = _cell_repr(lab[i][j])
            color = 0
            if ch == 'S':
                color = curses.color_pair(COLORS['start'])
            elif ch == 'E':
                color = curses.color_pair(COLORS['goal'])
            elif ch == SYMBOLS['wall']:
                color = curses.color_pair(COLORS['wall'])
            elif ch.isdigit() and ch not in ('0'):
                color = curses.color_pair(COLORS['weight'])

            y = top + i
            x = left + j * 2
            stdscr.attron(color)
            stdscr.addstr(y, x, ch)
            stdscr.attroff(color)

    for k in range(1, min(robot_idx + 1, len(path))):
        i, j = path[k]
        if lab[i][j] in ('S', 'E'):
            continue
        y = top + i
        x = left + j * 2
        stdscr.attron(curses.color_pair(COLORS['path']))
        stdscr.addstr(y, x, SYMBOLS['path'])
        stdscr.attroff(curses.color_pair(COLORS['path']))

    if 0 <= robot_idx < len(path):
        ri, rj = path[robot_idx]
        y = top + ri
        x = left + rj * 2
        stdscr.attron(curses.color_pair(COLORS['robot']))
        stdscr.addstr(y, x, SYMBOLS['robot'])
        stdscr.attroff(curses.color_pair(COLORS['robot']))


def _animate(stdscr, lab: List[List[str]], path: List[Pos], delay_ms: int):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(delay_ms)
    _init_colors()

    idx = 0
    while True:
        stdscr.erase()
        _draw_grid(stdscr, lab, path, idx)
        # Rodapé
        msg = f"passo {idx+1}/{len(path)} | delay={delay_ms}ms"
        h, w = stdscr.getmaxyx()
        stdscr.attron(curses.color_pair(COLORS['text']))
        stdscr.addstr(h - 1, max(0, (w - len(msg)) // 2), msg)
        stdscr.attroff(curses.color_pair(COLORS['text']))

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key in (ord('+'), ord('=')):
            delay_ms = max(10, delay_ms - 10)
            stdscr.timeout(delay_ms)
        elif key in (ord('-'), ord('_')):
            delay_ms = min(1000, delay_ms + 10)
            stdscr.timeout(delay_ms)
        elif key in (curses.KEY_RIGHT, ord('n')):
            idx = min(len(path) - 1, idx + 1)
        elif key in (curses.KEY_LEFT, ord('p')):
            idx = max(0, idx - 1)
        else:
            if idx < len(path) - 1:
                idx += 1
            else:
                time.sleep(2)
                break


def run_curses_animation(lab: List[List[str]], path: List[Pos], delay_ms: int = 120):
    curses.wrapper(_animate, lab, path, delay_ms)
