from pathlib import Path
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivymd.uix.label import MDIcon

lucide_path = Path(__file__).parent
Builder.load_file(str(lucide_path / "lucide.kv"))
LabelBase.register(
    name="Lucide",
    fn_regular=str(lucide_path / "lucide.ttf")
)

class LucideIcon(MDIcon):
    pass

# Generate icon_definitions.py
if __name__ == "__main__":
    from fontTools.ttLib import TTFont

    lucide = TTFont(lucide_path / "lucide.ttf")
    cmap = lucide.getBestCmap()
    icon_defs = {name: chr(code_point) for code_point, name in cmap.items()}

    with open(lucide_path / "icon_definitions.py", "w") as file:
        file.write(f"lucide_icons = {str(icon_defs)}")
