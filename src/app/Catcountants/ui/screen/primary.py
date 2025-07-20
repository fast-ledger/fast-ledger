from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from utilities.loadkv import loadkv

loadkv(__file__)

class PrimaryScreen(MDScreen):
    title = StringProperty()

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        """Change screen and title when switching tabs by bottom nav bar"""
        screen_manager = self.ids.primary_screen_manager
        current_index = screen_manager.screen_names.index(screen_manager.current)
        next_index = screen_manager.screen_names.index(item.get_screen_name())
        # Transition left or right based on order on navigation bar
        if current_index < next_index:
            screen_manager.transition.direction = 'left'
        else:
            screen_manager.transition.direction = 'right'
        screen_manager.current = item.get_screen_name()

        self.title = self.ids.primary_screen_manager.current_screen.title
