import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from todo import add, complete


def test_adding_a_task_keeps_existing_tasks():
    assert add([{"title": "a", "done": False}], " b ") == [{"title": "a", "done": False}, {"title": "b", "done": False}]


def test_blank_titles_are_rejected():
    with pytest.raises(ValueError):
        add([], "  ")


def test_completing_marks_only_the_chosen_task():
    items = add(add([], "a"), "b")
    assert [item["done"] for item in complete(items, 1)] == [False, True]
