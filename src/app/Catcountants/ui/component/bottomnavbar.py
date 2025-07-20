from kivy.properties import StringProperty
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from utilities.loadkv import loadkv

loadkv(__file__)

class CatNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()

class CatBottomNavBar(MDNavigationBar):
    pass