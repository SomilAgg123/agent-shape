def add(items, title):
    title = title.strip()
    if not title:
        raise ValueError("A task needs a title.")
    return [*items, {"title": title, "done": False}]


def complete(items, index):
    return [dict(item, done=True) if position == index else item for position, item in enumerate(items)]
