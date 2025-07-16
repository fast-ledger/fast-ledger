# screens/home_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.button import MDFloatingActionButton
from kivy.properties import StringProperty, NumericProperty

class HomeScreen(Screen):
    balance_text = StringProperty("123,456 NT$")
    total_expenses_text = StringProperty("23,456 NT$")

    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        print("進入首頁畫面")
        if 'bottom_nav_bar' in self.ids:
            self.ids.bottom_nav_bar.bind(on_tab_switch=self.on_bottom_nav_tab_switched)
            print("MDBottomNavigation 的 on_tab_switch 事件已綁定。")
        else:
            print("警告: 'bottom_nav_bar' ID 未在 .kv 中找到，無法綁定事件。")

    def on_bottom_nav_tab_switched(self, instance_bottom_navigation, item_widget, item_name):
        print(f"底部導航：'{item_name}' 被切換到")
        if item_name == 'home_nav':
            pass
        elif item_name == 'journal_nav':
            self.manager.current = 'journal_screen' # 已取消註銷
        elif item_name == 'report_nav':
            print("跳轉到 Report 頁面 (未實作)")
            pass
        elif item_name == 'settings_nav':
            print("跳轉到 Settings 頁面 (未實作)")
            pass

    def settings_button_pressed(self):
        print("設定按鈕被點擊！ (右上角)")

    def add_button_pressed(self):
        print("新增按鈕被點擊！ (FAB +)")

    def transaction_button_pressed(self):
        print("交易按鈕被點擊！ (FAB $)")
        self.manager.current = 'camera_screen'