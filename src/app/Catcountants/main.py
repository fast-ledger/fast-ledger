from kivy.lang import Builder
from kivymd.app import MDApp

class CatcountantsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"

        return Builder.load_file("main.kv")
    
if __name__ == "__main__":
    CatcountantsApp().run()