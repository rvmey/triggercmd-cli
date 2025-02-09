"""
TriggerCMD CLI

Linux CLI client to TriggerCMD cloud service agent.

You probably want to install completion for the typer command.
If you are using bash, try to type:

$ triggercmd --install-completion bash

https://github.com/GussSoares/triggercmd-cli
"""

import time

import typer
from rich.console import Console
from rich.table import Table

from triggercmd_cli.command.entities import Command, TriggerCMDAgent, TriggerCMDUI
from triggercmd_cli.command.wizard import CommandWizard
from triggercmd_cli.utils import exceptions, functions

command_app = typer.Typer(help=__doc__)
console = Console()


@command_app.command(help="Create a new command.")
def new():
    console.rule("Create a command")

    new = CommandWizard.new()

    with console.status("[yellow]Please wait...[/]"):
        time.sleep(5)
        Command.new(**new)

    message = f"\n[green]Success![/] Command `{new['trigger']}` created."
    console.print(message)
    console.rule()


@command_app.command(help="Edit a command existent.")
def edit():
    console.rule("Edit a command")

    commands = functions.get_command_titles()
    command_selected = CommandWizard.select_command(commands)
    edited = CommandWizard.edit(command_selected)

    with console.status("[yellow]Please wait...[/]"):
        time.sleep(5)
        Command.edit(command_selected["trigger"], edited)

    message = f"\n[green]Success![/] Command `{edited['trigger']}` edited."
    console.print(message)
    console.rule()


@command_app.command(help="Remove a command existent.")
def remove():
    console.rule("Remove a command")

    commands = functions.get_command_titles()
    selected = CommandWizard.select_command(commands)
    message = f"\n[green]Success![/] Command `{selected['trigger']}` removed."

    if CommandWizard.confirm("Are you sure you want remove this command?"):
        with console.status("[yellow]Please wait...[/]"):
            time.sleep(5)
            Command.remove(selected)

        console.print(message)
        console.rule()


@command_app.command(help="List all commands.")
def list():
    data = functions.load_json_file()

    table = Table(title="Command List", title_justify="center")
    table.add_column("Trigger")
    table.add_column("Command")
    table.add_column("Ground")
    table.add_column("Voice")
    table.add_column("Allow Params")

    for row in data:
        table.add_row(
            row.get("trigger"),
            row.get("command"),
            row.get("ground"),
            row.get("voice"),
            row.get("allowParams"),
        )

    console.print()
    console.rule("TriggerCMD")
    console.print(table)
    console.rule("")


@command_app.command(help="Test a command.")
def test(trigger: str = typer.Option("", help="Trigger name")):
    """
    It tests a command

    :param trigger: str = typer.Option("", help="Trigger name")
    :type trigger: str
    """

    console.rule("Test a command")

    if not trigger:
        commands = functions.get_command_titles()
        trigger = CommandWizard.select_command(commands).get("trigger")

    response, status = Command.test("ds", trigger)

    if status == 200:
        message = f"[green]Success[/] {response.get('message')}"
    else:
        message = f"[red]Error[/] {response.get('error')}"

    console.print(message)
    console.rule()


@command_app.command(help="Download and install TriggerCMD Agent")
def install_agent():
    console.rule("Installing")
    if CommandWizard.confirm("TriggerCMD will be installed in the user directory, do you want to continue?"):
        try:
            TriggerCMDAgent.clone()
        except exceptions.AlreadyCloned:
            console.print("[blue]Info:[/] TriggerCMD is already cloned, ignoring...\n")

        TriggerCMDAgent.install_dependecies()
        console.print("\n[green]Success![/] TriggerCMD Agent installed. Please type `triggercmd run`.")
    else:
        console.print("Exiting...")


@command_app.command(help="Uninstall TriggerCMD")
def uninstall():
    # TODO: remover atalho, agent, e so entao executa um pip uninstall
    console.rule("Uninstalling")
    TriggerCMDUI.remove_shortcut()
    # TriggerCMDAgent.uninstall()
    console.print("\n[green]Success![/] TriggerCMD Agent uninstalled. Now please type \"pip uninstall triggercmd\" to remove the CLI.")


@command_app.command(help="Install TriggerCMD Desktop App")
def install_app():
    console.rule("Installing")
    TriggerCMDUI.create_shortcut()
    console.print("\n[green]Success![/] TriggerCMD Desktop App installed. Please search by \"TriggerCMD App\".")


@command_app.command(help="Run TriggerCMD Agent")
def run():
    console.rule("Running")
    TriggerCMDAgent.run()


@command_app.command(help="Run TriggerCMD Desktop App")
def app(background: bool = False):
    """
    This function runs the UI

    :param background: bool = False, defaults to False
    :type background: bool (optional)
    """

    try:
        console.rule("Running UI")
        console.print("Type Ctrl+C to exit...")
        TriggerCMDUI().start_app(background=background)
    except KeyboardInterrupt:
        pass
