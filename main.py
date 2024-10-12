"""A simple example demonstrating chat functionality using x.ai API directly with streaming."""

import os
import json
import requests
import customer_service
import rich
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


def create_chat_completion(api_key, messages):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    data = {
        "messages": messages,
        "model": "grok-2-public",
        "stream": True,
    }

    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
                    chunk = json.loads(line)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]


if __name__ == "__main__":
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("API key not found in Secrets")
        exit()

    # Initialize the console
    console = Console()

    # Header Panel
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
    menu_table.add_row("2", "Exit")

    console.print(menu_table)

    # Prompt user for input
    console.print("\n[bold cyan]Select an option (1-2):[/] ", end="")
    option = input()

    # Processing input
    if option == "1":
        console.print(
            Panel(
                "[green]We'd love to hear your feedback![/]", border_style="green"
            )
        )
    elif option == "2":
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

    conversation = [{"role": "system", "content": "You are who you are."}]

    print("Enter an empty message to quit.\n")

    while True:
        user_input = input("Hello, please give us some feedback on our product: ")
        user_input += "Please give the output in JSON format with the format {message:}"
        print("")

        if not user_input:
            print("Empty input received. Exiting chat.")
            break

        conversation.append({"role": "user", "content": user_input})

        print("Support Bot: ", end="", flush=True)
        full_response = ""
        for token in create_chat_completion(api_key, conversation):
            full_response += token
        print("\n")

        customer_service.sayhi(full_response)
        conversation.append({"role": "assistant", "content": full_response})

    print("Thank you for using the customer service bot!")
