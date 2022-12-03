from dotenv import load_dotenv
import os
from canvasapi import Canvas
from canvasapi.todo import Todo
from bs4 import BeautifulSoup

import pytermgui as ptg

API_URL = "https://canvas.calpoly.edu/"


class Detail(ptg.Container):
    def set_todo(self, todo: Todo) -> None:
        description = BeautifulSoup(todo.assignment["description"]).text

        self.set_widgets(
            [
                ptg.Label(todo.context_name),
                ptg.Label(f"[bold]{todo.assignment['name']}[/]"),
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

    detail = Detail()

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
            box="SINGLE",
            vertical_align=ptg.VerticalAlignment.TOP,
        )
    )
    manager.add(
        ptg.Window(detail, box="SINGLE", vertical_align=ptg.VerticalAlignment.TOP)
    )
