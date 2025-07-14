# screens/home_screen.py
from kivy.uix.screenmanager import Screen

# 雖然這裡引入了 MDBottomNavigationItem 和 MDFloatingActionButton，
# 但實際上在 Python 檔案中直接引用它們，主要是為了類別定義，
# KivyMD 的 .kv 解析器會處理其大部分行為。
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.button import MDFloatingActionButton
from kivy.properties import StringProperty, NumericProperty  # 引入 Kivy 的屬性類型


class HomeScreen(Screen):
    # Kivy Properties 用於在 .kv 檔案中綁定顯示的動態數據
    balance_text = StringProperty("123,456 NT$")
    total_expenses_text = StringProperty("23,456 NT$")

    def __init__(self, **kw):
        """
        HomeScreen 類的初始化方法。
        Kivy 的 __init__ 方法通常用於設定 UI 元素的初始狀態或綁定。
        """
        super().__init__(**kw)
        # 在這裡通常不會直接操作 ids，因為此時 .kv 文件可能還未完全解析。
        # 綁定事件通常放在 on_enter 或 on_kv_post_load 等方法中。

    def on_enter(self, *args):
        """
        當此畫面成為 ScreenManager 的當前畫面時觸發。
        這是重新載入數據或執行畫面特定初始化邏輯的好時機。
        """
        print("進入首頁畫面")
        # 確保 self.ids 在 .kv 文件加載後可用
        # 我們將 bottom_nav_bar 的事件綁定放在這裡，以確保元件已準備好。
        if "bottom_nav_bar" in self.ids:
            # 綁定 on_tab_switch 事件到 on_bottom_nav_tab_switched 方法
            # Kivy 的 bind 方法會將事件相關的參數自動傳遞給回調函數。
            # on_tab_switch 的參數是 (instance_bottom_navigation, item_widget, item_name)
            self.ids.bottom_nav_bar.bind(on_tab_switch=self.on_bottom_nav_tab_switched)
            print("MDBottomNavigation 的 on_tab_switch 事件已綁定。")
        else:
            print("警告: 'bottom_nav_bar' ID 未在 .kv 中找到，無法綁定事件。")

    # 處理底部導航欄項目切換事件的回調方法
    # 更改方法名稱，以避免與 .kv 中的命名衝突，同時也更語義化
    def on_bottom_nav_tab_switched(
        self, instance_bottom_navigation, item_widget, item_name
    ):
        """
        處理底部導航欄項目切換事件。
        這個方法由 Python bind() 調用，接收三個參數。
        Args:
            instance_bottom_navigation: MDBottomNavigation 的實例。
            item_widget: 被選中的 MDBottomNavigationItem 實例。
            item_name (str): 被選中的 MDBottomNavigationItem 的 'name' 屬性。
        """
        print(f"底部導航：'{item_name}' 被切換到")
        # 根據 item_name 切換到不同的畫面。
        # 這些畫面也需要在 main.py 的 ScreenManager 中定義。
        if item_name == "home_nav":
            # 如果已經在首頁，可以選擇不做任何事或者強制刷新畫面
            pass
        elif item_name == "journal_nav":
            self.manager.current = (
                "journal_screen"  # 修正：取消註釋這行，實現跳轉到 'journal_screen'
            )
            print("跳轉到 Journal 頁面")
        elif item_name == "report_nav":
            # self.manager.current = 'report_screen' # 假設您有一個 'report_screen' 頁面
            print("跳轉到 Report 頁面 (未實作)")
            pass
        elif item_name == "settings_nav":
            # self.manager.current = 'settings_screen' # 假設您有一個 'settings_screen' 頁面
            print("跳轉到 Settings 頁面 (未實作)")
            pass

    # 其他按鈕的回調方法保持不變
    def settings_button_pressed(self):
        """
        處理右上角設定按鈕點擊事件。
        """
        print("設定按鈕被點擊！ (右上角)")
        # self.manager.current = 'settings_screen'

    def add_button_pressed(self):
        """
        處理中間的 '+' 懸浮動作按鈕 (FAB) 點擊事件。
        """
        print("新增按鈕被點擊！ (FAB +)")
        # self.manager.current = 'add_record_screen'

    def transaction_button_pressed(self):
        """
        處理中間下方的 '相機' 懸浮動作按鈕 (FAB) 點擊事件。
        點擊後跳轉到 camera_screen 畫面。
        """
        print("交易按鈕被點擊！ (FAB $)")
        self.manager.current = "camera_screen"
