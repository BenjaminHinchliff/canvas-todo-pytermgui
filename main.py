from typing import Any
from dotenv import load_dotenv
import os
from canvasapi import Canvas
from canvasapi.todo import Todo
from bs4 import BeautifulSoup
import dateutil.parser
import pytermgui as ptg

API_URL = "https://canvas.calpoly.edu/"
AM_PM = False


class Detail(ptg.Container):
    def __init__(self, **attrs: Any) -> None:
        super().__init__(**attrs)
        self.window = None

    def show(self, manager: ptg.WindowManager):
        if self.window is not None:
            self.window.close()
        self.window = ptg.Window(
            self,
            box=ptg.boxes.SINGLE,
            vertical_align=ptg.VerticalAlignment.TOP,
            width=60,
            height=30,
        ).center()
        manager.add(self.window)

    def set_todo(self, todo: Todo) -> None:
        assignment = todo.assignment
        # TODO: do something other than just deleting the html lol
        description = BeautifulSoup(
            assignment["description"], features="html.parser"
        ).text

        due_at = assignment["due_at"]
        if due_at is not None:
            # reformat time and convert from UTC to local timezone
            due_at = (
                dateutil.parser.isoparse(due_at)
                .astimezone()
                .strftime(
                    f"%a %b %d %Y {'%I' if AM_PM else '%H'}:%M {'%p' if AM_PM else ''}"
                )
            )

        self.set_widgets(
            [
                ptg.Label(todo.context_name),
                ptg.Label(f"[bold]{assignment['name']}[/]"),
                ptg.Label(
                    f"[italic][dim]Due {due_at}[/]" if due_at is not None else ""
                ),
                ptg.Label(""),
                ptg.Label(description),
            ]
        )


load_dotenv()

token = os.getenv("CANVAS_API_TOKEN")
if token is None:
    raise SystemExit("missing api token :(")

canvas = Canvas(API_URL, token)


with ptg.WindowManager() as manager:
    manager.layout.add_slot("Todos")
    # manager.layout.add_slot("Detail", width=)

    todos = canvas.get_todo_items()

    detail = Detail(box=ptg.boxes.EMPTY)

    todo_widgets = []
    for todo in todos:

        def handler(_, todo=todo):
            detail.show(manager)
            detail.set_todo(todo)

        button = ptg.Button(
            todo.assignment["name"],
            on_click=handler,
            parent_align=ptg.HorizontalAlignment.LEFT,
        )
        todo_widgets.append(button)

    manager.add(
        ptg.Window(
            *todo_widgets,
            box=ptg.boxes.EMPTY,
            vertical_align=ptg.VerticalAlignment.TOP,
        ),
        animate=False,
    )
