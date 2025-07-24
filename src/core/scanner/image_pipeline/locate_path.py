from pathlib import Path


def locate_path(path, show_msg=False):
    if path is None:
        if show_msg:
            print("Path is None")
        return None

    path = Path(path)

    if "*" in path.name:
        if Path(path.parent).exists():
            if show_msg:
                print(f"Path '{path}', is exist")
            return path
        else:
            if show_msg:
                print(f"No '{path}' found")
            return None

    if path.exists():
        if show_msg:
            print(f"Path: '{path}', is exist")
        return path
    else:
        if show_msg:
            print(f"No '{path}' found")
        return None
