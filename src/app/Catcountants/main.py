from pathlib import Path
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from utilities.loadkv import loadkv

loadkv(__file__)

class StackScreenManager(MDScreenManager):
    pass

class CatcountantsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        
        LabelBase.register(
            name="NotoSansCJK",
            fn_regular=str(Path(__file__).parent / "fonts/NotoSansCJK-Regular.ttf"),
            fn_bold=str(Path(__file__).parent / "fonts/NotoSansCJK-Bold.ttc"),
        )
        # Change app font to NotoSansCJK
        for style in self.theme_cls.font_styles:
            if style == "Icon": continue
            for role in self.theme_cls.font_styles[style]:
                self.theme_cls.font_styles[style][role]["font-name"] = "NotoSansCJK"

        return StackScreenManager()

if __name__ == "__main__":
    CatcountantsApp().run()