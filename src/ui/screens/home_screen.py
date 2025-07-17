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
        # 綁定底部導航欄的 tab 切換事件
        if 'bottom_nav_bar' in self.ids:
            self.ids.bottom_nav_bar.bind(on_tab_switch=self.on_bottom_nav_tab_switched)
            print("MDBottomNavigation 的 on_tab_switch 事件已綁定。")
        else:
            print("警告: 'bottom_nav_bar' ID 未在 .kv 中找到，無法綁定事件。")

    def on_bottom_nav_tab_switched(self, instance_bottom_navigation, item_widget, item_name):
        """
        處理底部導航欄的標籤切換事件。
        根據切換到的標籤名稱，更新 ScreenManager 的當前畫面。
        """
        print(f"底部導航：'{item_name}' 被切換到")
        if item_name == 'home_nav':
            # 如果是 Home 標籤，則保持在當前畫面或執行其他 Home 相關邏輯
            pass
        elif item_name == 'journal_nav':
            # 切換到 Journal 畫面
            self.manager.current = 'journal_screen'
        elif item_name == 'report_nav':
            print("跳轉到 Report 頁面 (未實作)")
            # self.manager.current = 'report_screen' # 如果有 report_screen，則取消註釋這行
            pass
        elif item_name == 'settings_nav':
            print("跳轉到 Settings 頁面 (未實作)")
            # self.manager.current = 'settings_screen' # 如果有 settings_screen，則取消註釋這行
            pass

    def settings_button_pressed(self):
        """
        處理頂部應用程式欄右側「設定」按鈕的點擊事件。
        """
        print("設定按鈕被點擊！ (右上角)")
        # self.manager.current = 'settings_screen' # 假設您要跳轉到設定畫面

    def add_button_pressed(self):
        """
        處理中間「新增」卡片（帶有加號圖標）的點擊事件。
        """
        print("新增按鈕被點擊！ (中間的加號卡片)")
        self.manager.current = 'transaction_screen' # 點擊新增按鈕跳轉到交易畫面

    def transaction_button_pressed(self):
        """
        處理懸浮動作按鈕 (FAB $ 或相機圖標) 的點擊事件。
        這個方法將負責切換到相機畫面。
        """
        print("交易按鈕被點擊！ (FAB 相機圖標)")
        self.manager.current = 'camera_screen' # 切換到相機畫面