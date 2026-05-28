"""
Console Utility
===============
Professional terminal output helpers: banners, section headers,
progress bars, and summary tables.
"""

from colorama import Fore, Back, Style, init
from tabulate import tabulate
from typing import Any, Dict, List, Optional

init(autoreset=True)

# ──────────────────────────────────────────────
# Width constants
# ──────────────────────────────────────────────
TERMINAL_WIDTH: int = 100
SEPARATOR_CHAR: str = "═"
THIN_SEP_CHAR: str = "─"


def print_banner(title: str, subtitle: str = "") -> None:
    """Print a full-width colored pipeline banner."""
    border = Fore.CYAN + SEPARATOR_CHAR * TERMINAL_WIDTH + Style.RESET_ALL
    padding = " " * ((TERMINAL_WIDTH - len(title)) // 2)
    print()
    print(border)
    print(Fore.CYAN + Style.BRIGHT + padding + title + Style.RESET_ALL)
    if subtitle:
        sub_padding = " " * ((TERMINAL_WIDTH - len(subtitle)) // 2)
        print(Fore.YELLOW + sub_padding + subtitle + Style.RESET_ALL)
    print(border)
    print()


def print_section(title: str) -> None:
    """Print a section header with thin separators."""
    sep = Fore.BLUE + THIN_SEP_CHAR * TERMINAL_WIDTH + Style.RESET_ALL
    print()
    print(sep)
    print(Fore.BLUE + Style.BRIGHT + f"  ▶  {title}" + Style.RESET_ALL)
    print(sep)


def print_success(message: str) -> None:
    """Print a green success message."""
    print(Fore.GREEN + Style.BRIGHT + f"  ✔  {message}" + Style.RESET_ALL)


def print_warning(message: str) -> None:
    """Print a yellow warning message."""
    print(Fore.YELLOW + Style.BRIGHT + f"  ⚠  {message}" + Style.RESET_ALL)


def print_error(message: str) -> None:
    """Print a red error message."""
    print(Fore.RED + Style.BRIGHT + f"  ✖  {message}" + Style.RESET_ALL)


def print_info(message: str) -> None:
    """Print a cyan informational message."""
    print(Fore.CYAN + f"  ℹ  {message}" + Style.RESET_ALL)


def print_kv(key: str, value: Any, indent: int = 4) -> None:
    """Print a key-value pair."""
    pad = " " * indent
    print(
        f"{pad}{Fore.WHITE}{Style.BRIGHT}{key:<35}{Style.RESET_ALL}"
        f"{Fore.YELLOW}{value}{Style.RESET_ALL}"
    )


def print_table(
    data: List[Dict[str, Any]],
    headers: Optional[List[str]] = None,
    title: str = "",
) -> None:
    """
    Print a formatted table using tabulate.

    Args:
        data: List of row dictionaries.
        headers: Column header labels (inferred from keys if None).
        title: Optional title printed above the table.
    """
    if not data:
        print_warning("No data to display in table.")
        return

    if title:
        print(Fore.CYAN + Style.BRIGHT + f"\n  {title}" + Style.RESET_ALL)

    if headers is None:
        headers = list(data[0].keys())

    rows = [[row.get(h, "") for h in headers] for row in data]
    print(
        Fore.WHITE
        + tabulate(rows, headers=headers, tablefmt="fancy_grid")
        + Style.RESET_ALL
    )
    print()


def print_dict_table(d: Dict[str, Any], title: str = "") -> None:
    """Print a two-column (Key | Value) table from a dict."""
    rows = [{"Key": k, "Value": v} for k, v in d.items()]
    print_table(rows, headers=["Key", "Value"], title=title)


def print_step(step_num: int, total: int, description: str) -> None:
    """Print a numbered pipeline step indicator."""
    pct = int((step_num / total) * 100)
    bar_filled = int(pct / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    print(
        f"\n  {Fore.CYAN}[{bar}] {pct:3d}%  "
        f"Step {step_num}/{total}: "
        f"{Fore.WHITE}{Style.BRIGHT}{description}{Style.RESET_ALL}"
    )
