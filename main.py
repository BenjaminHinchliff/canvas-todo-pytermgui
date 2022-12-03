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
    def set_todo(self, todo: Todo) -> None:
        assignment = todo.assignment
        # TODO: do something other than just deleting the html lol
        description = BeautifulSoup(assignment["description"]).text

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
    manager.layout.add_slot("Todos", width=0.3)
    manager.layout.add_slot("Detail")

    todos = canvas.get_todo_items()

    detail = Detail(box=ptg.boxes.EMPTY)

    todo_widgets = []
    for todo in todos:
        handler = lambda _, todo=todo: detail.set_todo(todo)
        button = ptg.Button(
            todo.assignment["name"],
            on_click=handler,
            parent_align=ptg.HorizontalAlignment.LEFT,
        )
        todo_widgets.append(button)

    manager.add(
        ptg.Window(
            *todo_widgets,
            box=ptg.boxes.SINGLE,
            vertical_align=ptg.VerticalAlignment.TOP,
        )
    )
    manager.add(
        ptg.Window(detail, box="SINGLE", vertical_align=ptg.VerticalAlignment.TOP)
    )
