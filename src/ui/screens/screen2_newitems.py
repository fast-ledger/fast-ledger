from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

class NewItemsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.title_label = Label(text="New Items", font_size='30sp', size_hint=(1, 0.1))
        self.layout.add_widget(self.title_label)

        self.all_options = [
            "Invoice Scanning System",
            "Data Account Book",
            "Keyword search: income and expenditure",
            "Weekly consumption records"
        ]
        self.available_options = self.all_options.copy()
        self.option_buttons = []

        self.add_widget(self.layout)

    def on_enter(self):
        self.refresh_options()

    def refresh_options(self):
        for btn in self.option_buttons:
            self.layout.remove_widget(btn)
        self.option_buttons.clear()

        if not self.available_options:
            self.title_label.text = "Nothing"
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'home'), 1)
            return
        else:
            self.title_label.text = "New Items"

        for option in sorted(self.available_options):
            btn = Button(text=option, font_size='20sp', size_hint=(1, 0.15))
            btn.bind(on_press=self.option_selected)
            self.layout.add_widget(btn)
            self.option_buttons.append(btn)

    def option_selected(self, instance):
        selected_text = instance.text
        home_screen = self.manager.get_screen('home')
        home_screen.add_dynamic_button(selected_text)
        if selected_text in self.available_options:
            self.available_options.remove(selected_text)
        self.manager.current = 'home'
