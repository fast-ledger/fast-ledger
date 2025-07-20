# ui/screens/transaction_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivymd.uix.chip import MDChip
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import MDList, TwoLineListItem

# 修正導入路徑
from kivymd.uix.pickers import MDDatePicker 
from kivymd.uix.pickers import MDTimePicker 

import datetime

# KV 文件將從 ui/kv/transaction_screen.kv 載入，由 main.py 統一處理

class CreditorInputField(MDBoxLayout):
    field_name = StringProperty("")
    field_value = StringProperty("")
    # 新增一個屬性來控制輸入框的提示文本
    hint_text = StringProperty("") 

    def on_field_name(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_field_label_text(value), 0)

    def _update_field_label_text(self, value):
        if self.ids and 'field_label' in self.ids:
            if self.ids.field_label.text != value:
                self.ids.field_label.text = value

    def on_field_value(self, instance, value):
        Clock.schedule_once(lambda dt: self._update_text_input_text(value), 0)

    def _update_text_input_text(self, value):
        if self.ids and 'text_input' in self.ids:
            if self.ids.text_input.text != value:
                self.ids.text_input.text = value

class IndustryTag(MDChip):
    tag_text = StringProperty("")
    remove_callback = None

class CreditorSection(MDBoxLayout):
    name_value = StringProperty('')
    uniform_number_value = StringProperty('')
    business_person_value = StringProperty('')
    industry_tags = ListProperty([])
    # 將 is_main_organization_checkbox_active 從這裡移除，移到 CreditorDetailWidget
    # is_main_organization_checkbox_active = BooleanProperty(False) 

    def on_industry_tags(self, instance, value):
        self.update_industry_tags_ui()
        # 觸發父級 (CreditorDetailWidget) 調整高度
        if self.parent and hasattr(self.parent, '_adjust_height_after_tag_change'):
            self.parent._adjust_height_after_tag_change()

    def add_industry_tag(self, tag_text):
        tag_text = tag_text.strip()
        if tag_text and tag_text not in self.industry_tags:
            self.industry_tags.append(tag_text)
            print(f"CreditorSection: Added tag: {tag_text}. Current tags: {self.industry_tags}")

    def remove_industry_tag(self, chip_instance):
        if chip_instance.tag_text in self.industry_tags:
            self.industry_tags.remove(chip_instance.tag_text)
            print(f"CreditorSection: Removed tag: {chip_instance.tag_text}. Current tags: {self.industry_tags}")

    def update_industry_tags_ui(self):
        print(f"CreditorSection: update_industry_tags_ui called for {self}")
        Clock.schedule_once(lambda dt: self._do_update_industry_tags_ui(), 0)

    def _do_update_industry_tags_ui(self):
        if not self.ids or 'industry_tags_layout' not in self.ids:
            print(f"CreditorSection: Warning: industry_tags_layout ID not found in {self} during UI update.")
            return

        layout = self.ids.industry_tags_layout
        input_box = None
        
        # 尋找並暫存輸入框，避免被 clear_widgets 移除
        for child in list(layout.children):
            if isinstance(child, MDBoxLayout) and \
               any(isinstance(c, MDTextField) for c in child.children) and \
               any(isinstance(c, MDIconButton) for c in child.children):
                input_box = child
                layout.remove_widget(input_box)
                break
            
        layout.clear_widgets() # 清除所有標籤

        for tag in self.industry_tags:
            chip = IndustryTag(tag_text=tag)
            chip.remove_callback = self.remove_industry_tag
            layout.add_widget(chip)

        # 重新添加輸入框
        if input_box:
            layout.add_widget(input_box)


class CreditorDetailWidget(MDBoxLayout):
    main_org_name = StringProperty('')
    main_org_uniform_number = StringProperty('')
    main_org_business_person = StringProperty('')
    main_org_industry_tags = ListProperty([])
    # 新增屬性用於判斷主機構是否同總機構
    main_org_is_main_organization = BooleanProperty(True) 

    branch_org_name = StringProperty('')
    branch_org_uniform_number = StringProperty('')
    branch_org_business_person = StringProperty('')
    branch_org_industry_tags = ListProperty([])

    cancel_callback = ObjectProperty(None)
    save_callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._post_init, 0)

    def _post_init(self, dt):
        print("CreditorDetailWidget: _post_init called")
        if self.ids and 'main_organization_section' in self.ids and \
           'branch_organization_section' in self.ids:
            main_section = self.ids.main_organization_section
            branch_section = self.ids.branch_organization_section

            # 將 Checkbox 的綁定移到這裡
            if 'main_org_checkbox' in self.ids:
                self.ids.main_org_checkbox.bind(
                    active=self._on_main_org_checkbox_change
                )
                # 初始根據 main_org_is_main_organization 設定 checkbox 狀態
                self.ids.main_org_checkbox.active = self.main_org_is_main_organization
                self._on_main_org_checkbox_change(
                    self.ids.main_org_checkbox,
                    self.ids.main_org_checkbox.active
                )
            else:
                print("CreditorDetailWidget: Warning: main_org_checkbox ID not found.")
            
            main_section.update_industry_tags_ui()
            branch_section.update_industry_tags_ui()
        else:
            print("CreditorDetailWidget: Warning: main_organization_section or branch_organization_section ID not found, rescheduling _post_init.")
            Clock.schedule_once(self._post_init, 0.1)


    def _on_main_org_checkbox_change(self, instance, value):
        print(f"CreditorDetailWidget: _on_main_org_checkbox_change called, value: {value}")
        # 將 value 直接賦予到 class 屬性，以便 get_creditor_data 獲取
        self.main_org_is_main_organization = value 
        if not self.ids or 'branch_organization_section' not in self.ids:
            print("CreditorDetailWidget: Warning: branch_organization_section ID not found during checkbox change.")
            return

        branch_section = self.ids.branch_organization_section
        branch_title_label = self.ids.branch_title_label # 獲取分支機構標題
        
        if value: # 如果 '同總機構' 被勾選 (即主機構就是總機構)
            branch_section.disabled = True
            branch_section.height = 0
            branch_section.opacity = 0
            branch_title_label.height = 0 # 隱藏標題
            branch_title_label.opacity = 0 # 隱藏標題
            # 清空分支機構數據
            self.branch_org_name = ""
            self.branch_org_uniform_number = ""
            self.branch_org_business_person = ""
            self.branch_org_industry_tags = []
        else: # 如果 '同總機構' 未被勾選 (即存在分支機構)
            branch_section.disabled = False
            branch_section.opacity = 1
            branch_section.height = branch_section.minimum_height
            branch_title_label.height = branch_title_label.texture_size[1] # 顯示標題
            branch_title_label.opacity = 1 # 顯示標題
            branch_section.update_industry_tags_ui()
        
        Clock.schedule_once(lambda dt: self._trigger_parent_height_adjustment(), 0.1)


    def _trigger_parent_height_adjustment(self):
        print("CreditorDetailWidget: _trigger_parent_height_adjustment called")
        if self.parent and hasattr(self.parent, 'height'):
            # 確保 content_cls 的高度正確，以便 MDDialog 可以調整
            self.height = self.minimum_height 
            if hasattr(self.parent, 'parent') and isinstance(self.parent.parent, MDDialog):
                 dialog_parent = self.parent.parent
                 dialog_parent.size_hint_y = None
                 # 重新計算 dialog 的高度：內容高度 + dialog 自身的 padding 和按鈕區高度
                 dialog_parent.height = self.minimum_height + dp(80) # 預留底部按鈕和額外padding
                 print(f"CreditorDetailWidget: Adjusted MDDialog height to {dialog_parent.height}.")
            else:
                print("CreditorDetailWidget: Not an MDDialog parent or parent structure unexpected.")
        else:
            print("CreditorDetailWidget: Warning: Parent or its height not found for adjustment.")


    def _adjust_height_after_tag_change(self):
        Clock.schedule_once(lambda dt: self._trigger_parent_height_adjustment(), 0.1)

    def set_creditor_data(self, main_org_data, branch_org_data=None):
        print(f"CreditorDetailWidget: set_creditor_data called. Main: {main_org_data}, Branch: {branch_org_data}")
        # 主機構數據
        self.main_org_name = main_org_data.get('name', '')
        self.main_org_uniform_number = main_org_data.get('uniform_number', '')
        self.main_org_business_person = main_org_data.get('business_person', '')
        self.main_org_industry_tags = main_org_data.get('industry_tags', [])
        # 設置同總機構複選框狀態
        self.main_org_is_main_organization = main_org_data.get('is_main_organization', True)
        if self.ids and 'main_org_checkbox' in self.ids:
            self.ids.main_org_checkbox.active = self.main_org_is_main_organization
        
        # 分支機構數據
        if branch_org_data:
            self.branch_org_name = branch_org_data.get('name', '')
            self.branch_org_uniform_number = branch_org_data.get('uniform_number', '')
            self.branch_org_business_person = branch_org_data.get('business_person', '')
            self.branch_org_industry_tags = branch_org_data.get('industry_tags', [])
        else:
            # 如果沒有分支機構數據，確保清空
            self.branch_org_name = ""
            self.branch_org_uniform_number = ""
            self.branch_org_business_person = ""
            self.branch_org_industry_tags = []

        # 在數據設置後，確保 UI 更新和高度調整
        Clock.schedule_once(lambda dt: self._post_set_data_ui_update(), 0.1)

    def _post_set_data_ui_update(self, dt):
        print("CreditorDetailWidget: _post_set_data_ui_update called")
        if self.ids and 'main_organization_section' in self.ids and 'branch_organization_section' in self.ids:
            self.ids.main_organization_section.update_industry_tags_ui()
            self.ids.branch_organization_section.update_industry_tags_ui()
            # 重新觸發 checkbox 的 on_change 事件以正確調整分支機構的顯示狀態和高度
            if 'main_org_checkbox' in self.ids:
                self._on_main_org_checkbox_change(self.ids.main_org_checkbox, self.ids.main_org_checkbox.active)
            self._trigger_parent_height_adjustment()
        else:
            print("CreditorDetailWidget: Warning: Sections not ready for UI update after data set. Retrying...")
            Clock.schedule_once(self._post_set_data_ui_update, 0.1)


    def get_creditor_data(self):
        data = {
            'main_organization': {
                'name': self.ids.main_organization_section.name_value,
                'uniform_number': self.ids.main_organization_section.uniform_number_value,
                'business_person': self.ids.main_organization_section.business_person_value,
                'industry_tags': self.ids.main_organization_section.industry_tags,
                'is_main_organization': self.main_org_is_main_organization # 從這裡獲取狀態
            }
        }
        if not self.main_org_is_main_organization: # 如果不是同總機構，則讀取分支機構數據
            data['branch_organization'] = {
                'name': self.ids.branch_organization_section.name_value,
                'uniform_number': self.ids.branch_organization_section.uniform_number_value,
                'business_person': self.ids.branch_organization_section.business_person_value,
                'industry_tags': self.ids.branch_organization_section.industry_tags,
                'is_main_organization': False
            }
        return data


class TransactionItem(MDBoxLayout):
    item_name = StringProperty("")
    tag_text = StringProperty("") # 這個將會綁定到 MDTextField
    amount = StringProperty("")

class TransactionAccountItem(MDBoxLayout):
    account_name = StringProperty("")
    tag_text = StringProperty("") # 這個將會綁定到 MDTextField
    amount = StringProperty("")
    can_edit = BooleanProperty(False) # 暫時保留，但可能在 UI 調整後不使用


class TransactionScreen(MDScreen):
    dialog = None
    creditor_dialog = None
    # time_dialog = None # 不再需要這個，因為 MDDatePicker/MDTimePicker 直接打開
    selected_date = ObjectProperty(datetime.date.today())
    selected_time = ObjectProperty(datetime.datetime.now().time())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creditor_data = {
            'main_organization': {
                'name': '尚未設定',
                'uniform_number': '',
                'business_person': '',
                'industry_tags': [],
                'is_main_organization': True
            }
        }
        Clock.schedule_once(self._update_initial_ui, 0)
        
    def _update_initial_ui(self, dt):
        self.update_creditor_display()
        self.update_time_display()

    def update_creditor_display(self):
        main_org = self.creditor_data.get('main_organization', {})
        branch_org = self.creditor_data.get('branch_organization', None)

        display_text = main_org.get('name', '尚未設定')
        if branch_org and not main_org.get('is_main_organization', True):
            display_text += f"\n(分支: {branch_org.get('name', 'N/A')})"
        
        if self.ids and 'creditor_name_display' in self.ids:
            self.ids.creditor_name_display.text = display_text
            print(f"更新借方顯示為: {display_text}")
        else:
            print("Warning: creditor_name_display ID not found to update.")

    def update_time_display(self):
        if self.selected_date and self.selected_time:
            display_datetime = datetime.datetime.combine(self.selected_date, self.selected_time)
            display_text = display_datetime.strftime("%Y-%m-%d %H:%M")
            if self.ids and 'transaction_time_display' in self.ids:
                self.ids.transaction_time_display.text = display_text
                print(f"更新時間顯示為: {display_text}")
            else:
                print("Warning: transaction_time_display ID not found to update.")

    def show_creditor_dialog(self):
        print("TransactionScreen: show_creditor_dialog called")
        # 每次都創建新的 CreditorDetailWidget 以確保數據和 UI 的初始狀態正確
        content_widget = CreditorDetailWidget(
            cancel_callback=self.dismiss_creditor_dialog,
            save_callback=self.save_creditor_data
        )

        self.creditor_dialog = MDDialog(
            title="借方資料",
            type="custom",
            content_cls=content_widget,
            auto_dismiss=False,
            size_hint=(0.9, None) # 初始高度會根據內容自適應，由 content_cls 內部調整
        )
        
        main_org_data = self.creditor_data.get('main_organization', {})
        branch_org_data = self.creditor_data.get('branch_organization')

        # 在 dialog 打開後設置數據，確保 content_cls 完全初始化
        Clock.schedule_once(lambda dt: self._set_creditor_dialog_data(main_org_data, branch_org_data), 0.2) 

        self.creditor_dialog.open()

    def _set_creditor_dialog_data(self, main_org_data, branch_org_data):
        if self.creditor_dialog and self.creditor_dialog.content_cls:
            print("TransactionScreen: Setting creditor dialog data.")
            self.creditor_dialog.content_cls.set_creditor_data(
                main_org_data, branch_org_data
            )
        else:
            print("TransactionScreen: Warning: Creditor dialog or content_cls not ready to set data. Retrying...")
            Clock.schedule_once(lambda dt: self._set_creditor_dialog_data(main_org_data, branch_org_data), 0.1)


    def dismiss_creditor_dialog(self):
        print("TransactionScreen: dismiss_creditor_dialog called")
        if self.creditor_dialog:
            self.creditor_dialog.dismiss()
            self.creditor_dialog = None # 清空引用

    def save_creditor_data(self):
        print("TransactionScreen: save_creditor_data called")
        if self.creditor_dialog and self.creditor_dialog.content_cls:
            self.creditor_data = self.creditor_dialog.content_cls.get_creditor_data()
            self.update_creditor_display()
            print(f"儲存的借方資料: {self.creditor_data}")
            self.dismiss_creditor_dialog()

    def show_time_dialog(self):
        print("TransactionScreen: show_time_dialog called")
        # 直接使用正確的導入路徑
        # from kivymd.uix.pickers import MDDatePicker # 已經在文件開頭導入
        # from kivymd.uix.pickers import MDTimePicker # 已經在文件開頭導入

        date_dialog = MDDatePicker(
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day
        )
        date_dialog.bind(on_save=self.on_date_save, on_cancel=self.on_time_dialog_cancel) #
        date_dialog.open() #

    def on_date_save(self, instance, value, date_range):
        print(f"Selected Date: {value}")
        self.selected_date = value
        
        # from kivymd.uix.pickers import MDTimePicker # 已經在文件開頭導入
        time_dialog = MDTimePicker() #
        time_dialog.set_time(self.selected_time) #
        time_dialog.bind(on_save=self.on_time_save, on_cancel=self.on_time_dialog_cancel) #
        time_dialog.open() #

    def on_time_save(self, instance, value):
        print(f"Selected Time: {value}")
        self.selected_time = value
        self.update_time_display()

    def on_time_dialog_cancel(self, instance, value=None): #
        # 當日期或時間選擇器被取消時調用
        print("時間選擇器已取消。") #

    def add_new_item(self):
        print("TransactionScreen: add_new_item called")
        # 這裡可以實現添加新交易項目的邏輯，例如彈出一個對話框
        # 創建一個新的 TransactionItem
        new_item = TransactionItem(
            item_name="新項目",
            tag_text="expenses:new:category",
            amount="NT$ 0"
        )
        # 將新項目添加到 transaction_items 佈局的頂部
        # 因為 Kivy 佈局是從後往前添加的，所以要 insert(0) 才能顯示在最上面
        self.ids.transaction_items.add_widget(new_item, len(self.ids.transaction_items.children) - 2)
        # 讓滾動視圖滾動到最底部以顯示新添加的項目
        Clock.schedule_once(lambda dt: self.ids.content_scroll_view.scroll_to(new_item), 0.1)


    def edit_last_item(self):
        print("TransactionScreen: edit_last_item called")
        # 實現編輯最後一個交易項目的邏輯
        # 假設我們編輯列表中的第一個 TransactionItem (因為 KV 中倒序定義)
        # 如果您想編輯視覺上的最後一個項目，您需要遍歷 `self.ids.transaction_items.children`
        # 找到第一個 TransactionItem 或 TransactionAccountItem
        
        # 簡單示例：編輯列表中的第一個可編輯項目 (假設是應收帳款)
        if len(self.ids.transaction_items.children) > 0:
            # Kivy BoxLayout 的 children 列表是倒序的
            # 最頂部的項目在列表的末尾
            # 如果要編輯視覺上的 "最後一個"，那就是 KV 定義中的 "活期存款"
            # 它在 children 列表中的位置是倒數第一個
            last_item_widget = self.ids.transaction_items.children[0] 
            
            if isinstance(last_item_widget, TransactionAccountItem):
                print(f"編輯最後一個項目: {last_item_widget.account_name}")
                # 這裡可以彈出編輯對話框或啟用編輯模式
                # 簡單示範修改值
                # last_item_widget.amount = "NT$ -350"
                # last_item_widget.tag_text = "assets:current:checking:modified"
                app = MDApp.get_running_app()
                app.show_alert_dialog(f"編輯項目: {last_item_widget.account_name}\n(功能待完善)")
            else:
                print("最後一個項目不是 TransactionAccountItem，無法編輯。")
        else:
            print("沒有可編輯的交易項目。")


    def cancel_transaction(self):
        print("TransactionScreen: cancel_transaction called")
        # 重置借方數據
        self.creditor_data = {
            'main_organization': {
                'name': '尚未設定',
                'uniform_number': '',
                'business_person': '',
                'industry_tags': [],
                'is_main_organization': True
            }
        }
        self.update_creditor_display()

        # 重置時間數據
        self.selected_date = datetime.date.today()
        self.selected_time = datetime.datetime.now().time()
        self.update_time_display()

        # 清除動態添加的交易項目，保留 KV 中定義的初始項目
        if self.ids and 'transaction_items' in self.ids:
            # 根據 KV 檔案，初始有 5 個項目 (3個TransactionItem, 2個TransactionAccountItem)
            # children 列表是倒序的，所以 KV 中最後定義的會在 children[0]
            # 我們需要保留最 "舊" 的 5 個項目
            
            # 這裡需要一個更穩健的方法來判斷哪些是初始項目，哪些是動態添加的
            # 一種方法是，在動態添加時給它們一個特定的標記
            # 或者，簡單地清除所有並重新加載初始項目 (這可能需要從 KV 重新構建)
            # 目前，暫時只清空 '新添加' 的部分，這需要知道有多少個是預先定義在KV中的。
            # 假設 KV 中有 5 個預設項目
            initial_items_count = 5 
            current_children = list(self.ids.transaction_items.children)
            # children 是倒序的，所以從索引 0 開始移除，直到剩下 initial_items_count
            while len(self.ids.transaction_items.children) > initial_items_count:
                # 移除最頂部的元素 (在 children 列表中是最後一個)
                self.ids.transaction_items.remove_widget(self.ids.transaction_items.children[-1])
            print("Transaction items cleared, keeping initial KV defined items.")


    def save_transaction(self):
        print("TransactionScreen: save_transaction called")
        
        print(f"Final Creditor Data: {self.creditor_data}")
        print(f"Final Transaction Time: {self.selected_date} {self.selected_time}")
        
        transaction_items_list = []
        if self.ids and 'transaction_items' in self.ids:
            # 遍歷所有交易項目，收集它們的數據
            # 注意：children 列表是反向的 (最後加入的在最前面)
            for item_widget in reversed(self.ids.transaction_items.children): # 使用 reversed 確保按順序讀取
                if isinstance(item_widget, TransactionItem):
                    transaction_items_list.append({
                        'type': 'item',
                        'name': item_widget.item_name,
                        'tag': item_widget.ids.tag_text_input.text, # 從 MDTextField 獲取文本
                        'amount': item_widget.amount
                    })
                elif isinstance(item_widget, TransactionAccountItem):
                    transaction_items_list.append({
                        'type': 'account',
                        'name': item_widget.account_name,
                        'tag': item_widget.ids.tag_text_input.text, # 從 MDTextField 獲取文本
                        'amount': item_widget.amount
                    })
        print(f"Final Transaction Items: {transaction_items_list}")

        # 保存後重置並返回主頁
        self.cancel_transaction()
        MDApp.get_running_app().go_to_home_screen()


    def on_search_creditor(self):
        print("TransactionScreen: on_search_creditor called")
        pass

    def search_button_pressed(self):
        print("TransactionScreen: search_button_pressed called from TopAppBar")
        pass

    def settings_button_pressed(self):
        print("TransactionScreen: settings_button_pressed called from TopAppBar")
        pass

    def go_to_camera_screen(self):
        print("TransactionScreen: go_to_camera_screen called from FAB")
        MDApp.get_running_app().go_to_camera_screen()

    # ====== 新增的方法來處理返回鍵邏輯 ======
    def go_back_to_home_and_reset(self):
        """
        處理返回按鈕，執行取消交易並返回主頁的動作。
        """
        print("TransactionScreen: go_back_to_home_and_reset called.")
        self.cancel_transaction() # 首先取消交易並重置
        MDApp.get_running_app().go_to_home_screen() # 然後跳轉回主頁