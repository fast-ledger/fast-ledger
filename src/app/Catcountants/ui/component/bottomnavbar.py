from kivy.properties import StringProperty
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from utilities.loadkv import loadkv

loadkv(__file__)

class CatNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()

    def get_screen_name(self):
        return self.text.lower()

class CatBottomNavBar(MDNavigationBar):
    pass