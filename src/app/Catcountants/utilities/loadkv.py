from pathlib import Path
from kivy.lang import Builder

def loadkv(path):
    py_path = Path(path)
    Builder.load_file(str(py_path.parent / py_path.stem) + ".kv")