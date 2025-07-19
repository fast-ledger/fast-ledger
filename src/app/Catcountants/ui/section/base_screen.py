from pathlib import Path
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

Builder.load_file(str(Path(__file__).parent / "base_screen.kv"))

class BaseScreen(MDScreen):
    pass