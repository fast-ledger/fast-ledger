from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen

Builder.load_file("main.kv")

class BaseScreen(MDScreen):
    pass

class StackScreenManager(MDScreenManager):
    pass

class CatcountantsApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"

        return StackScreenManager()

if __name__ == "__main__":
    CatcountantsApp().run()