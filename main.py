"""A simple example demonstrating chat functionality using x.ai API directly with streaming."""

import os
import json
import requests
import post_consumer
import grok
import rich
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from time import sleep


if __name__ == "__main__":
    # Header Panel
    console = Console()
    console.print(
        Panel(
            Text(
                "✨ Customer Feedback Service ✨",
                justify="center",
                style="bold white on purple",
            ),
            title="Welcome",
            title_align="center",
            border_style="green",
        )
    )

    # Feedback Service Menu
    menu_table = Table(title="Menu", box=box.SIMPLE_HEAD, style="bright_blue")
    menu_table.add_column("Option", justify="center", style="bold cyan")
    menu_table.add_column("Description", justify="center", style="bold yellow")

    menu_table.add_row("1", "Give Product Feedback")
    menu_table.add_row("2", "(Advanced) Start Backend Tweet Consumer")
    menu_table.add_row("3", "Exit")

    console.print(menu_table)

    # Prompt user for input
    console.print("\n[bold cyan]Select an option (1-2):[/] ", end="")
    option = input()

    # Start the CLI Interfae
    if option == "1":
        console.print(
            Panel(
                "[green]We'd love to hear your feedback![/]", border_style="green"
            )
        )

        grok.startchat()


    elif option == "2":
        # Start the consumer service
        post_consumer.start_poll()
    elif option == "3":
        console.print(
            Panel(
                "[magenta]Thank you for using the service. Goodbye![/]",
                border_style="magenta",
            )
        )
        exit()
    else:
        console.print(
            Panel(
                "[red]Invalid option. Please select a valid option.[/]",
                border_style="red",
            )
        )

    