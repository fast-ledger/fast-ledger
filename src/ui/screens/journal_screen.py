# screens/journal_screen.py
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivy.properties import ListProperty, StringProperty
from kivymd.app import MDApp # 引入 MDApp 以便在需要時訪問應用程式實例

class JournalScreen(Screen):
    # 用於儲存交易數據的 Kivy Property
    transactions_data = ListProperty([])

    def __init__(self, **kw):
        super().__init__(**kw)
        print("JournalScreen 初始化")

    def on_enter(self, *args):
        print("進入帳本畫面")
        self.load_transactions()
        if 'bottom_nav_bar' in self.ids:
            self.ids.bottom_nav_bar.bind(on_tab_switch=self.on_bottom_nav_tab_switched)
            print("JournalScreen: MDBottomNavigation 的 on_tab_switch 事件已綁定。")
        else:
            print("JournalScreen 警告: 'bottom_nav_bar' ID 未在 .kv 中找到，無法綁定事件。")

    def load_transactions(self):
        self.ids.transaction_list.clear_widgets()

        mock_data = [
            {"date": "2025-07-11", "description": "好初早餐店", "category": "expenses:food:dining:lunch", "amount": "120"},
            {"date": "2025-07-11", "description": "FamilyMart 全家便利商店", "category": "expenses:food:drink:coffee", "amount": "35"},
            {"date": "2025-07-10", "description": "綠葉生活事業股份有限公司", "category": "expenses:food:groceries", "amount": "195"},
            {"date": "2025-07-10", "description": "三商餐飲股份有限公司", "category": "expenses:food:dining:dinner", "amount": "109", "account": "liabilities:payable:accounts:a"},
            {"date": "2025-07-10", "description": "誠品生活股份有限公司", "category": "appearance:clothing", "amount": "200"},
            {"date": "2025-07-10", "description": "MWD 豪味煲", "category": "expenses:food:dining:lunch", "amount": "75", "account": "assets:current:jkpay", "amount2": "75", "account2": "assets:current:jkpay", "amount3": "-75", "account3": "assets:current:jkpay"},
            {"date": "2025-07-09", "description": "大潤發 RT-MART", "category": "expenses:food:groceries", "amount": "62"},
            {"date": "2025-07-09", "description": "大潤發 RT-MART", "category": "expenses:food:drink:packaged", "amount": "41"},
            {"date": "2025-07-09", "description": "大潤發 RT-MART", "category": "expenses:receivable:accounts:a", "amount": "25", "account": "assets:current:checking"},
            {"date": "2025-07-09", "description": "Recharge EasyCard", "category": "assets:current:EasyCard", "amount": "300"},
            {"date": "2025-07-09", "description": "Withdraw | ATM : 中國信託銀行", "category": "assets:current:cash", "amount": "5000", "account": "expenses:fee:withdraw", "amount2": "5", "account2": "assets:current:checking"},
            {"date": "2025-07-08", "description": "兩塊5分錢", "category": "expenses:food:drink:tea shop", "amount": "30"},
            {"date": "2025-07-08", "description": "兩塊5分錢", "category": "assets:receivable:accounts:a", "amount": "30", "account": "assets:current:cash"},
        ]

        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.color_definitions import colors

        for item_data in mock_data:
            main_item_text = f"{item_data.get('date', '未知日期')} {item_data.get('description', '無描述')}"
            
            list_item = OneLineAvatarIconListItem(
                text=main_item_text,
                bg_color=[0.95, 0.95, 0.95, 1],
                on_release=self.on_transaction_item_click
            )
            list_item.add_widget(IconRightWidget(icon="chevron-right", theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1]))

            full_secondary_text = f"{item_data.get('category', '無類別')}\n" \
                                  f"NT$ {item_data.get('amount', '')}"
            if 'account' in item_data:
                full_secondary_text += f" {item_data['account']}"
            if 'amount2' in item_data:
                full_secondary_text += f"\nNT$ {item_data['amount2']} {item_data.get('account2', '')}"
            if 'amount3' in item_data:
                full_secondary_text += f"\nNT$ {item_data['amount3']} {item_data.get('account3', '')}"

            list_item.secondary_text = full_secondary_text
            list_item.secondary_font_style = "Caption"

            self.ids.transaction_list.add_widget(list_item)


    def on_transaction_item_click(self, instance):
        print(f"交易項目 '{instance.text}' 被點擊了！")

    def on_bottom_nav_tab_switched(self, instance_bottom_navigation, item_widget, item_name):
        print(f"JournalScreen: 底部導航 '{item_name}' 被切換到")
        if item_name == 'home_nav':
            self.manager.current = 'home_screen'
        elif item_name == 'journal_nav':
            pass
        elif item_name == 'report_nav':
            self.manager.current = 'report_screen'
        elif item_name == 'settings_nav':
            self.manager.current = 'settings_screen'

    def search_button_pressed(self):
        print("搜尋按鈕被點擊！ (Journal)")

    def journal_settings_button_pressed(self):
        print("帳本設定按鈕被點擊！ (Journal)")

    def add_transaction_fab_pressed(self):
        print("新增交易 FAB ($) 被點擊！ (Journal)")
        self.manager.current = 'camera_screen'