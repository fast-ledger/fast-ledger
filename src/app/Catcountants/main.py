from pathlib import Path
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

Builder.load_file("main.kv")

class StackScreenManager(MDScreenManager):
    pass

class CatcountantsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        
        LabelBase.register(
            name="NotoSansCJK",
            fn_regular=str(Path(__file__).parent / "fonts/NotoSansCJK-Regular.ttf")
        )
        # Change app font to NotoSansCJK
        for style in self.theme_cls.font_styles:
            if style == "Icon": continue
            for role in self.theme_cls.font_styles[style]:
                self.theme_cls.font_styles[style][role]["font-name"] = "NotoSansCJK"

        return StackScreenManager()

if __name__ == "__main__":
    CatcountantsApp().run()