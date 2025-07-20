# screens/journal_screen.py
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem # 引入列表項
from kivymd.uix.card import MDCard # 引入 MDCard
from kivymd.uix.boxlayout import MDBoxLayout # 引入 MDBoxLayout
from kivymd.uix.label import MDLabel # 引入 MDLabel
from kivymd.uix.dialog import MDDialog # 引入 MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton # 引入按鈕
from kivymd.uix.textfield import MDTextField # 引入文字輸入框
from kivymd.uix.pickers import MDDatePicker # 引入日期選擇器
from kivymd.uix.chip import MDChip # 引入 MDChip
from kivymd.uix.gridlayout import MDGridLayout # 引入 MDGridLayout
from kivymd.uix.button import MDIconButton # 引入圖標按鈕
from kivy.clock import Clock # 用於延遲執行
from kivy.metrics import dp # 引入 dp 函數用於適應性尺寸

import datetime # 用於日期處理


class SearchTransactionContent(MDBoxLayout):
    """
    搜尋交易浮動視窗的內容佈局。
    包含輸入框、日期選擇器和標籤添加功能。
    """
    search_name = StringProperty('')
    search_date = ObjectProperty(None) # 用於儲存選中的日期
    search_amount = StringProperty('')
    search_category = StringProperty('') # 新增：搜尋類別
    search_tags = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_date = datetime.date.today() # 預設為今天
        Clock.schedule_once(self._update_date_display, 0) # 初始化後更新日期顯示

    def _update_date_display(self, dt):
        if self.ids and 'date_display_label' in self.ids:
            self.ids.date_display_label.text = self.search_date.strftime("%Y-%m-%d")

    def show_date_picker(self):
        """顯示日期選擇器"""
        date_dialog = MDDatePicker(
            year=self.search_date.year,
            month=self.search_date.month,
            day=self.search_date.day
        )
        date_dialog.bind(on_save=self.on_date_save, on_cancel=self.on_date_cancel)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        """日期選擇器保存時的回調"""
        self.search_date = value
        self._update_date_display(0) # 更新日期顯示

    def on_date_cancel(self, instance, value):
        """日期選擇器取消時的回調"""
        print("日期選擇器已取消。")

    def add_tag_from_input(self, text_input_instance):
        """從 MDTextField 添加標籤"""
        tag_text = text_input_instance.text.strip()
        if tag_text and tag_text not in self.search_tags:
            self.search_tags.append(tag_text)
            print(f"Added search tag: {tag_text}. Current tags: {self.search_tags}")
            text_input_instance.text = "" # 清空輸入框
            self.update_tags_ui() # 更新 UI

    def remove_tag(self, chip_instance):
        """移除選中的標籤"""
        # chip_instance.text 實際是 MDChip 的 text 屬性，它已經是標籤內容
        tag_to_remove = chip_instance.text
        if tag_to_remove in self.search_tags:
            self.search_tags.remove(tag_to_remove)
            print(f"Removed search tag: {tag_to_remove}. Current tags: {self.search_tags}")
            self.update_tags_ui() # 更新 UI

    def update_tags_ui(self):
        """動態更新標籤顯示"""
        if not self.ids or 'tags_layout' not in self.ids:
            print("Warning: tags_layout ID not found during UI update.")
            return

        layout = self.ids.tags_layout
        input_box = None
        
        # 暫存輸入框及其父 MDBoxLayout
        for child in list(layout.children):
            if isinstance(child, MDBoxLayout) and \
               any(isinstance(c, MDTextField) for c in child.children) and \
               any(isinstance(c, MDIconButton) for c in child.children):
                input_box = child
                layout.remove_widget(input_box)
                break
            
        layout.clear_widgets() # 清除所有舊標籤

        for tag in self.search_tags:
            chip = MDChip(
                text=tag,
                icon='close-circle',
                on_release=self.remove_tag, # 直接綁定 remove_tag 方法，MDChip 實例會作為參數傳入
                font_name="NotoSansCJK" 
            )
            chip.text_color = [0, 0, 0, 1] # 黑色文字
            chip.md_bg_color = [0.8, 0.8, 0.8, 1] # 灰色背景
            layout.add_widget(chip)

        # 重新添加輸入框
        if input_box:
            layout.add_widget(input_box)
        
        # 調整父級對話框的高度
        Clock.schedule_once(lambda dt: self.parent_dialog_adjust_height(), 0.1)

    def parent_dialog_adjust_height(self):
        """通知父級 MDDialog 調整其高度以適應內容變化"""
        if self.parent and hasattr(self.parent, 'height'):
            # 確保 content_cls 的高度正確，以便 MDDialog 可以調整
            self.height = self.minimum_height 
            if hasattr(self.parent, 'parent') and isinstance(self.parent.parent, MDDialog):
                 dialog_parent = self.parent.parent
                 dialog_parent.size_hint_y = None
                 # 重新計算 dialog 的高度：內容高度 + dialog 自身的 padding 和按鈕區高度
                 # 這裡預估一個合適的底部 padding，具體數值可能需要微調
                 dialog_parent.height = self.minimum_height + dp(80) 
                 print(f"SearchTransactionContent: Adjusted MDDialog height to {dialog_parent.height}.")
            else:
                print("SearchTransactionContent: Not an MDDialog parent or parent structure unexpected.")
        else:
            print("SearchTransactionContent: Warning: Parent or its height not found for adjustment.")


    def get_search_criteria(self):
        """獲取搜尋條件"""
        return {
            'name': self.ids.name_input.text.strip(),
            'date': self.search_date.strftime("%Y-%m-%d"),
            'amount': self.ids.amount_input.text.strip(),
            'category': self.ids.category_input.text.strip(), # 新增：獲取類別
            'tags': self.search_tags[:] # 返回副本，避免外部修改
        }

    def set_search_criteria(self, criteria):
        """設置搜尋條件（用於編輯現有搜尋）"""
        self.ids.name_input.text = criteria.get('name', '')
        # 確保日期是 datetime.date 對象
        date_str = criteria.get('date', datetime.date.today().strftime("%Y-%m-%d"))
        try:
            self.search_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            self.search_date = datetime.date.today() # 無效日期則設為今天

        self.ids.amount_input.text = criteria.get('amount', '')
        self.ids.category_input.text = criteria.get('category', '') # 新增：設定類別
        self.search_tags = criteria.get('tags', [])
        self._update_date_display(0)
        self.update_tags_ui()


class JournalScreen(Screen):
    journal_data = ListProperty([]) # 原始數據
    filtered_journal_data = ListProperty([]) # 過濾後的數據
    search_dialog = None # 新增搜尋對話框實例

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._all_journal_data = [] # 用於存儲所有原始數據

    def on_enter(self, *args):
        print("進入帳本畫面") 
        # 僅在第一次進入時加載原始數據，之後使用過濾後的數據
        if not self._all_journal_data:
            self._all_journal_data = self._get_mock_journal_data() # 加載模擬數據
        self.display_journal_data(self._all_journal_data) # 預設顯示所有數據

    def _get_mock_journal_data(self):
        """
        模擬從圖片中提取的數據，用於內部存儲。
        """
        return [
            {"date": "2025-07-11", "description": "好初早餐店", "category": "飲食", "expenses": "food:dining:lunch", "assets": "assets:current:cash", "amount": "NT$ 120", "item_type": "ThreeLine"}, 
            {"date": "2025-07-11", "description": "FamilyMart 全家便利商店", "category": "飲食", "expenses": "food:drink:coffee", "assets": "assets:current:cash", "amount": "NT$ 35", "item_type": "ThreeLine"}, 
            {"date": "2025-07-10", "description": "統康生活事業股份有限公司", "category": "飲食", "expenses": "food:groceries", "assets": "assets:current:checking", "amount": "NT$ 195", "item_type": "ThreeLine"}, 
            {"date": "2025-07-10", "description": "三商餐飲股份有限公司", "category": "飲食", "expenses": "food:dining:dinner", "liabilities": "liabilities:payable:accounts:a", "amount": "NT$ 109", "item_type": "ThreeLine"}, 
            {"date": "2025-07-10", "description": "誠品生活股份有限公司", "category": "服飾", "expenses": "appearance:clothing", "assets": "assets:current:checking", "amount": "NT$ 200", "item_type": "ThreeLine"}, 
            {"date": "2025-07-10", "description": "MWD 客來發", "category": "飲食", "expenses": "food:dining:lunch", "assets1": "assets:current:jkpay", "amount1": "NT$ 75", "assets2": "assets:current:checking", "amount2": "NT$ 75", "assets3": "assets:current:jkpay", "amount3": "NT$ -75", "item_type": "MultiLine"}, 
            {"date": "2025-07-09", "description": "大潤發 RT-MART", "category": "購物", "expenses1": "food:groceries", "amount1": "NT$ 62", "expenses2": "food:drink:packaged", "amount2": "NT$ 41", "expenses3": "food:treats", "amount3": "NT$ 25", "assets1": "assets:receivable:accounts:a", "amount4": "NT$ 200", "assets2": "assets:current:checking", "amount5": "NT$ -328", "item_type": "MultiLine"}, 
            {"date": "2025-07-09", "description": "Recharge EasyCard", "category": "交通", "assets": "assets:current:EasyCard", "amount": "NT$ 300", "item_type": "ThreeLine"}, 
            {"date": "2025-07-09", "description": "Withdraw | ATM: 中國信託銀行", "category": "提款", "assets1": "assets:current:cash", "amount1": "NT$ 5000", "expenses": "expenses:fee:withdraw", "amount2": "NT$ 5", "assets2": "assets:current:checking", "item_type": "MultiLine"}, 
            {"date": "2025-07-08", "description": "再轉5分鐘", "category": "其他", "assets": "assets:current", "amount": "NT$ 100", "item_type": "ThreeLine"}, 
        ]

    def display_journal_data(self, data_list):
        """
        根據提供的數據列表更新顯示。
        """
        print("更新帳本顯示...") 
        if 'journal_list' in self.ids and self.ids.journal_list: 
            self.ids.journal_list.clear_widgets() 

            if not data_list: # 如果過濾後沒有數據
                self.ids.journal_list.add_widget(
                    MDLabel(text="沒有符合條件的帳本資料", halign='center', valign='middle', font_style='Caption', color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="50dp", font_name="NotoSansCJK")
                )
                print("沒有符合條件的帳本資料。")
                return

            for item_data in data_list: 
                card_layout = self.create_journal_entry_card(item_data) 
                self.ids.journal_list.add_widget(card_layout) 
        print("帳本顯示更新完成。") 


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
                                   font_size="16sp", bold=True, size_hint_x=0.7, font_name="NotoSansCJK")) 
        top_box.add_widget(MDLabel(text="", halign='right', size_hint_x=0.3)) # 右側預留空間 
        card.add_widget(top_box) 

        # 根據數據的複雜度添加多行 
        if data.get('item_type') == "ThreeLine": 
            card.height = "120dp" # 標準三行卡片高度 
            # 確保鍵存在才嘗試訪問
            if data.get('expenses'):
                card.add_widget(MDLabel(text=f"expenses:{data['expenses']}", font_size="14sp", color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="20dp", font_name="NotoSansCJK")) 
            mid_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp") 
            if data.get('assets'):
                mid_box.add_widget(MDLabel(text=f"assets:{data['assets']}", font_size="14sp", color=[0.5, 0.5, 0.5, 1], font_name="NotoSansCJK")) 
            if data.get('amount'):
                mid_box.add_widget(MDLabel(text=f"{data['amount']}", halign='right', font_size="14sp", bold=True, font_name="NotoSansCJK")) 
            card.add_widget(mid_box) 
            if data.get('liabilities'): # 如果有 liabilities 額外顯示 
                card.add_widget(MDLabel(text=f"liabilities:{data['liabilities']}", font_size="14sp", color=[0.5, 0.5, 0.5, 1], size_hint_y=None, height="20dp", font_name="NotoSansCJK")) 
                card.height = "140dp" # 增加一行的高度 

        elif data.get('item_type') == "MultiLine": 
            # 為多行數據動態創建標籤 
            current_height = 80 # 基礎高度 + 頂部 
            # 遍歷可能的關鍵字和數字對
            prefix_pairs = [
                ('expenses', 'amount'),
                ('assets', 'amount'),
                ('liabilities', 'amount')
            ]
            
            seen_items = set() # 用於防止重複添加，因為數據鍵可能有多個
            
            for key_prefix, amount_prefix in prefix_pairs:
                for i in range(1, 6): # 假設最多有5組，例如 expenses1, expenses2...
                    item_key = f"{key_prefix}{i}" if i > 1 else key_prefix
                    amount_key = f"{amount_prefix}{i}" if i > 1 else amount_prefix

                    item_value = data.get(item_key)
                    amount_value = data.get(amount_key)

                    if item_value and amount_value:
                        # 創建一個唯一標識符，防止同一組數據被重複處理
                        unique_id = f"{item_key}:{amount_key}"
                        if unique_id not in seen_items:
                            item_text = f"{key_prefix}:{item_value}"
                            item_amount = f"NT$ {amount_value}"
                            
                            line_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp") 
                            line_box.add_widget(MDLabel(text=item_text, font_size="14sp", color=[0.5, 0.5, 0.5, 1], font_name="NotoSansCJK")) 
                            line_box.add_widget(MDLabel(text=item_amount, halign='right', font_size="14sp", bold=True, font_name="NotoSansCJK")) 
                            card.add_widget(line_box) 
                            current_height += 25 # 每增加一行增加高度
                            seen_items.add(unique_id)
            card.height = f"{current_height}dp" # 設置最終高度 

        return card 

    def show_search_dialog(self):
        """顯示搜尋交易的浮動視窗"""
        print("顯示搜尋交易對話框。")
        if not self.search_dialog:
            self.search_dialog_content = SearchTransactionContent()
            self.search_dialog = MDDialog(
                title="搜尋交易",
                type="custom",
                content_cls=self.search_dialog_content,
                buttons=[
                    MDFlatButton(
                        text="取消",
                        on_release=self.dismiss_search_dialog,
                        font_name="NotoSansCJK" 
                    ),
                    MDRectangleFlatButton(
                        text="搜尋",
                        on_release=self.perform_search,
                        font_name="NotoSansCJK" 
                    ),
                ],
                auto_dismiss=False,
                size_hint=(0.9, None) # 初始高度會由 content_cls 調整
                # title_font_name="NotoSansCJK" # 此屬性在 KivyMD 1.1.1 中不支援，已移除
            )
            # 在打開對話框後，觸發內容的高度調整
            Clock.schedule_once(lambda dt: self.search_dialog_content.parent_dialog_adjust_height(), 0.1)

        self.search_dialog.open()

    def dismiss_search_dialog(self, *args):
        """關閉搜尋交易浮動視窗"""
        print("關閉搜尋交易對話框。")
        if self.search_dialog:
            self.search_dialog.dismiss()
            # self.search_dialog = None # 不清空引用，以便再次打開時保留上次的輸入

    def perform_search(self, *args):
        """執行搜尋操作，並關閉浮動視窗"""
        if self.search_dialog and self.search_dialog.content_cls:
            search_criteria = self.search_dialog.content_cls.get_search_criteria()
            print(f"執行搜尋，條件: {search_criteria}")
            
            # 執行過濾邏輯
            self.filtered_journal_data = self._filter_journal_data(search_criteria)
            self.display_journal_data(self.filtered_journal_data) # 顯示過濾後的數據

            self.dismiss_search_dialog()
        else:
            print("無法獲取搜尋條件或對話框內容不存在。")

    def _filter_journal_data(self, criteria):
        """
        根據搜尋條件過濾 journal_data。
        """
        filtered_data = []
        name_filter = criteria['name'].lower()
        date_filter = criteria['date'] # 日期已是 'YYYY-MM-DD' 格式
        amount_filter = criteria['amount'].replace('NT$', '').strip() # 移除 NT$
        category_filter = criteria['category'].lower()
        tags_filter = [tag.lower() for tag in criteria['tags']]

        for item in self._all_journal_data:
            match = True

            # 1. 名稱 (description) 模糊匹配
            if name_filter and name_filter not in item.get('description', '').lower():
                match = False
            
            # 2. 日期精確匹配 (如果日期有輸入)
            if date_filter and item.get('date') != date_filter:
                match = False

            # 3. 金額匹配 (精確匹配，如果金額有輸入)
            if amount_filter:
                # 處理金額格式，例如 "NT$ 120" 或 "NT$ -328"
                item_amount_str = item.get('amount', '').replace('NT$', '').strip()
                if item_amount_str != amount_filter:
                    match = False

            # 4. 類別 (category) 模糊匹配
            if category_filter and category_filter not in item.get('category', '').lower():
                match = False

            # 5. 科目 (tags) 匹配：只要有任一標籤匹配即可
            if tags_filter:
                item_tags = []
                # 提取 item 中所有可能的科目相關字符串
                for key, value in item.items():
                    if 'expenses' in key or 'assets' in key or 'liabilities' in key:
                        if isinstance(value, str):
                            item_tags.append(value.lower())
                
                # 檢查是否有任何一個搜尋標籤存在於 item 的科目中
                if not any(tag in item_tag for tag in tags_filter for item_tag in item_tags):
                    match = False

            if match:
                filtered_data.append(item)
        
        return filtered_data


    def search_button_pressed(self):
        """處理頂部搜尋按鈕的點擊事件，顯示搜尋對話框"""
        print("帳本搜尋按鈕被點擊！") 
        self.show_search_dialog()

    def settings_button_pressed(self):
        print("帳本設定按鈕被點擊！") 
        # 實現設定邏輯 
    
    def go_to_camera_screen(self):
        print("跳轉到相機畫面") 
        self.manager.current = 'camera_screen'