import math
import os

def rgb_to_ansi(r, g, b):
    """Convert RGB values to ANSI color code"""
    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"

def reset_color():
    """Reset terminal color"""
    return "\033[0m"

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except:
        return 80, 24

def clear_screen():
    """Clear terminal screen efficiently"""
    print("\033[H\033[2J", end="")

def hide_cursor():
    """Hide terminal cursor"""
    print("\033[?25l", end="")

def show_cursor():
    """Show terminal cursor"""
    print("\033[?25h", end="")

def move_cursor_home():
    """Move cursor to top-left without clearing"""
    print("\033[H", end="")