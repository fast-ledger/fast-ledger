# screens/journal_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem # 引入列表項
from kivymd.uix.card import MDCard # 引入 MDCard
from kivymd.uix.boxlayout import MDBoxLayout # 引入 MDBoxLayout
from kivymd.uix.label import MDLabel # 引入 MDLabel

class JournalScreen(Screen):
    # 用於在 .kv 檔案中動態顯示帳本條目的屬性
    # 這裡使用 ListProperty 來存儲要顯示的數據
    # 每個項目可以是字典，包含 'text', 'secondary_text', 'tertiary_text', 'right_text' 等
    journal_data = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化時可以加載一些預設數據或調用加載方法
        # 由於 Kivy 的生命週期，在 __init__ 中直接操作 self.ids 可能會失敗
        # 更好的做法是在 on_kv_post_load 或 on_enter 中處理

    def on_enter(self, *args):
        """
        當此畫面成為 ScreenManager 的當前畫面時觸發。
        這是加載或更新帳本數據的好時機。
        """
        print("進入帳本畫面")
        self.load_journal_data() # 調用加載數據的方法

        # 如果您希望在 Journal 頁面切換底部導航欄時，也能跳轉到對應頁面，
        # 並且這些頁面的切換邏輯是共用的，則可以在這裡獲取並設置底部導航欄的回調。
        # 但通常 MDBottomNavigation 是在 MDApp 層級管理的，而不是每個 Screen 獨立管理。
        # 這裡的邏輯會比較依賴 main.py 如何處理底部導航。

    def load_journal_data(self):
        """
        加載帳本數據並更新 journal_data 屬性。
        這裡只是模擬數據，實際應用中會從資料庫或文件加載。
        """
        print("加載帳本數據...")
        # 清空現有列表
        # 確保 self.ids.journal_list 在 .kv 文件加載後可用
        if 'journal_list' in self.ids and self.ids.journal_list:
            self.ids.journal_list.clear_widgets()

        # 模擬從圖片中提取的數據
        mock_data = [
            {"date": "2025-07-11", "description": "好初早餐店", "expenses": "food:dining:lunch", "assets": "assets:current:cash", "amount": "NT$ 120", "item_type": "ThreeLine"},
            {"date": "2025-07-11", "description": "FamilyMart 全家便利商店", "expenses": "food:drink:coffee", "assets": "assets:current:cash", "amount": "NT$ 35", "item_type": "ThreeLine"},
            {"date": "2025-07-10", "description": "統康生活事業股份有限公司", "expenses": "food:groceries", "assets": "assets:current:checking", "amount": "NT$ 195", "item_type": "ThreeLine"},
            {"date": "2025-07-10", "description": "三商餐飲股份有限公司", "expenses": "food:dining:dinner", "liabilities": "liabilities:payable:accounts:a", "amount": "NT$ 109", "item_type": "ThreeLine"},
            {"date": "2025-07-10", "description": "誠品生活股份有限公司", "expenses": "appearance:clothing", "assets": "assets:current:checking", "amount": "NT$ 200", "item_type": "ThreeLine"},
            {"date": "2025-07-10", "description": "MWD 客來發", "expenses": "food:dining:lunch", "assets1": "assets:current:jkpay", "amount1": "NT$ 75", "assets2": "assets:current:checking", "amount2": "NT$ 75", "assets3": "assets:current:jkpay", "amount3": "NT$ -75", "item_type": "MultiLine"}, # 特殊處理多行
            {"date": "2025-07-09", "description": "大潤發 RT-MART", "expenses1": "food:groceries", "amount1": "NT$ 62", "expenses2": "food:drink:packaged", "amount2": "NT$ 41", "expenses3": "food:treats", "amount3": "NT$ 25", "assets1": "assets:receivable:accounts:a", "amount4": "NT$ 200", "assets2": "assets:current:checking", "amount5": "NT$ -328", "item_type": "MultiLine"}, # 特殊處理多行
            {"date": "2025-07-09", "description": "Recharge EasyCard", "assets": "assets:current:EasyCard", "amount": "NT$ 300", "item_type": "ThreeLine"},
            {"date": "2025-07-09", "description": "Withdraw | ATM: 中國信託銀行", "assets1": "assets:current:cash", "amount1": "NT$ 5000", "expenses": "expenses:fee:withdraw", "amount2": "NT$ 5", "assets2": "assets:current:checking", "item_type": "MultiLine"}, # 特殊處理多行
            {"date": "2025-07-08", "description": "再轉5分鐘", "assets": "assets:current", "amount": "NT$ 100", "item_type": "ThreeLine"}, # 假設這個是簡化的
        ]

        if 'journal_list' in self.ids and self.ids.journal_list:
            for item_data in mock_data:
                # 為了更好的重現圖片中的效果，我們自定義一個 ListItem 的方式
                card_layout = self.create_journal_entry_card(item_data)
                self.ids.journal_list.add_widget(card_layout)

        if 'journal_list' in self.ids and not self.ids.journal_list.children:
            # 如果沒有任何項目，顯示「目前沒有帳本資料」
            self.ids.journal_list.add_widget(
                # 將 MDLabel 的所有參數寫在同一行，避免語法錯誤
                MDLabel(text="目前沒有帳本資料", halign='center', valign='middle', font_style='Caption', color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="50dp")
            )
        print("帳本數據加載完成。")

    def create_journal_entry_card(self, data):
        """
        根據數據創建一個類似圖片中交易條目的 MDCard。
        """
        card = MDCard(
            orientation='vertical',
            padding="10dp",
            spacing="5dp",
            size_hint_y=None,
            height="120dp", # 調整高度以適應內容，這裡先給個大概值
            md_bg_color=[1, 1, 1, 1], # 白色背景
            radius=[18, 18, 18, 18],
            elevation=1
        )
        card.bind(minimum_height=card.setter('height')) # 讓卡片高度適應內容

        # 日期和簡短描述
        top_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp")
        top_box.add_widget(MDLabel(text=f"{data.get('date', '')} {data.get('description', '')}",
                                   font_size="16sp", bold=True, size_hint_x=0.7))
        top_box.add_widget(MDLabel(text="", halign='right', size_hint_x=0.3)) # 右側預留空間
        card.add_widget(top_box)

        # 根據數據的複雜度添加多行
        if data.get('item_type') == "ThreeLine":
            card.height = "120dp" # 標準三行卡片高度
            card.add_widget(MDLabel(text=f"expenses:{data.get('expenses', '')}", font_size="14sp", color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="20dp"))
            mid_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp")
            mid_box.add_widget(MDLabel(text=f"assets:{data.get('assets', '')}", font_size="14sp", color=[0.5, 0.5, 0.5, 1]))
            mid_box.add_widget(MDLabel(text=f"{data.get('amount', '')}", halign='right', font_size="14sp", bold=True))
            card.add_widget(mid_box)
            if data.get('liabilities'): # 如果有 liabilities 額外顯示
                card.add_widget(MDLabel(text=f"liabilities:{data.get('liabilities', '')}", font_size="14sp", color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="20dp"))
                card.height = "140dp" # 增加一行的高度

        elif data.get('item_type') == "MultiLine":
            # 為多行數據動態創建標籤
            current_height = 80 # 基礎高度 + 頂部
            for key in data:
                if key.startswith('expenses') or key.startswith('assets') or key.startswith('liabilities'):
                    if not key.endswith('amount'): # 排除 amount 字段
                        amount_key = key.replace('expenses', 'amount').replace('assets', 'amount').replace('liabilities', 'amount')
                        amount = data.get(amount_key, '')
                        if amount: # 確保有金額才顯示
                            item_text = f"{key.split(':')[0]}:{data[key]}"
                            item_amount = f"NT$ {amount}"
                            line_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp")
                            line_box.add_widget(MDLabel(text=item_text, font_size="14sp", color=[0.5, 0.5, 0.5, 1]))
                            line_box.add_widget(MDLabel(text=item_amount, halign='right', font_size="14sp", bold=True))
                            card.add_widget(line_box)
                            current_height += 25 # 每增加一行增加高度
            card.height = f"{current_height}dp" # 設置最終高度

        return card

    def search_button_pressed(self):
        print("帳本搜尋按鈕被點擊！")
        # 實現搜尋邏輯

    def settings_button_pressed(self):
        print("帳本設定按鈕被點擊！")
        # 實現設定邏輯
    
    # <--- 新增此方法來處理跳轉到 CameraScreen --->
    def go_to_camera_screen(self):
        print("跳轉到相機畫面")
        self.manager.current = 'camera_screen'
