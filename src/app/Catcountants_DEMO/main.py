# main.py
# your_receipt_scanner_project/main.py
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivy.core.window import Window

Window.size = (1280, 750)


# 這些導入保持不變，因為我們暫時不調用它們的功能
# from ocr_processor.main_ocr_logic import OCRProcessor
# from nlp_processor.main_nlp_logic import NLPProcessor


# 定義 MainScreen 類別
class MainScreen(MDScreen):
    pass


class ReceiptScannerApp(MDApp):
    # KivyMD 屬性，用於從 KV 檔案中獲取 UI 元件的引用
    camera_widget = ObjectProperty(None)
    processed_image_widget = ObjectProperty(None)

    # OCR 內容的標籤，用來動態更新文本
    invoice_number_label = ObjectProperty(None)
    time_label = ObjectProperty(None)
    business_name_label = ObjectProperty(None)
    industry_label = ObjectProperty(None)

    # 為每個品項的名稱和分類創建單獨的 ObjectProperty
    item1_name_label = ObjectProperty(None)
    item1_category_label = ObjectProperty(None)
    item2_name_label = ObjectProperty(None)
    item2_category_label = ObjectProperty(None)
    item3_name_label = ObjectProperty(None)
    item3_category_label = ObjectProperty(None)
    # 更多品項，如果需要的話
    item4_name_label = ObjectProperty(None)
    item4_category_label = ObjectProperty(None)
    item5_name_label = ObjectProperty(None)
    item5_category_label = ObjectProperty(None)
    item6_name_label = ObjectProperty(None)
    item6_category_label = ObjectProperty(None)  # 修正此行

    def build(self):
        # 載入 KV 檔案，它會定義 MainScreen 的結構
        Builder.load_file("ui.kv")
        # 直接返回 MainScreen 的實例作為應用程式的根
        return MainScreen()

    def on_start(self):
        if self.root:
            # 直接透過 self.root.ids 存取所有 ID
            self.camera_widget = self.root.ids.camera_input
            self.processed_image_widget = self.root.ids.processed_image

            self.invoice_number_label = self.root.ids.invoice_number_label
            self.time_label = self.root.ids.time_label
            self.business_name_label = self.root.ids.business_name_label
            self.industry_label = self.root.ids.industry_label

            # 綁定新的品項名稱和分類 Label
            self.item1_name_label = self.root.ids.item1_name_label
            self.item1_category_label = self.root.ids.item1_category_label
            self.item2_name_label = self.root.ids.item2_name_label
            self.item2_category_label = self.root.ids.item2_category_label
            self.item3_name_label = self.root.ids.item3_name_label
            self.item3_category_label = self.root.ids.item3_category_label
            self.item4_name_label = self.root.ids.item4_name_label
            self.item4_category_label = self.root.ids.item4_category_label
            self.item5_name_label = self.root.ids.item5_name_label
            self.item5_category_label = self.root.ids.item5_category_label
            self.item6_name_label = self.root.ids.item6_name_label
            self.item6_category_label = self.root.ids.item6_category_label

            print("UI 元件綁定完成。")
            # 在應用程式啟動時，呼叫 clear_display 來初始化所有顯示
            self.clear_display()

        else:
            print("錯誤：應用程式根部件未設置。")

    def clear_display(self):
        """
        清除所有顯示的文字內容，實現初始化效果。
        """
        print("--- 呼叫 clear_display: 正在清除所有顯示內容 ---")
        self.invoice_number_label.text = "統一編號: "
        self.time_label.text = "時間: "
        self.business_name_label.text = "營業人名稱: "
        self.industry_label.text = "行業: "

        # 設置初始提示文本
        self.item1_name_label.text = "品項: (這裡放品項)"
        self.item1_category_label.text = "預測內容: (這裡放預測內容)"
        self.item2_name_label.text = ""
        self.item2_category_label.text = ""
        self.item3_name_label.text = ""
        self.item3_category_label.text = ""
        self.item4_name_label.text = ""
        self.item4_category_label.text = ""
        self.item5_name_label.text = ""
        self.item5_category_label.text = ""
        self.item6_name_label.text = ""
        self.item6_category_label.text = ""

        self.processed_image_widget.source = "assets/images/placeholder.png"  # "src/core/qrcode_scanner/receipt/Receipt_2.jpg"    # 確保顯示佔位圖
        print("--- 介面已重置為空白狀態 ---")

    def process_image_and_data(self):
        """
        這個方法現在只是一個佔位符，不執行實際的 OCR/NLP 處理。
        現在會被「掃描發票」按鈕調用。
        """
        print("--- process_image_and_data 被調用 ---")
        self.clear_display()  # <--- 關鍵：先清空所有現有內容

        # 模擬一些 OCR 數據用於發票資訊、品項和分類
        sample_ocr_data = {
            "invoice_number": "91601740",
            "time": "2025/01/07 15:18",
            "business_name": "歐立食品股份有限公司南勢角門市部",
            "industry": "未分類其他食品、飲料及菸草製品零售\n咖啡館",
            "items": [
                {"name": "玻璃 - 樹頂蘋果汁300ml", "category": "expenses:food:drink"},
                {"name": "肉鬆堡", "category": "expenses:food:treats"},
                {"name": "脆皮泡芙 (草莓)", "category": "expenses:food:dessert"},
                {"name": "咖啡拿鐵一杯", "category": "expenses:food:drink"},
                {"name": "綜合三明治", "category": "expenses:food:meal"},
                {"name": "計程車費用", "category": "expenses:transportation:taxi"},
            ],
        }
        self.update_ocr_display(sample_ocr_data)  # 呼叫更新所有數據的方法

        print("--- 模擬數據已載入並更新介面 ---")

    def _perform_processing(self):
        """
        這個方法現在是一個空的佔位符。
        """
        print("--- _perform_processing 被調用，但目前不執行任何操作 ---")
        pass  # 不執行任何操作

    def update_ocr_display(self, ocr_data):
        """
        更新 UI 中的 OCR 數據，包括發票資訊、品項和分類資訊。
        """
        print("--- update_ocr_display 被調用，正在更新發票資訊、品項和預測分類 ---")

        # 更新發票資訊標籤
        self.invoice_number_label.text = (
            f"統一編號: {ocr_data.get('invoice_number', '')}"
        )
        self.time_label.text = f"時間: {ocr_data.get('time', '')}"
        self.business_name_label.text = f"{ocr_data.get('business_name', '')}"
        self.industry_label.text = f"{ocr_data.get('industry', '')}"

        # 更新品項標籤
        items = ocr_data.get("items", [])

        # 為每個品項和其分類單獨設置文本
        # 使用一個列表來管理品項和分類的 Label 對，以便於遍歷和設置
        item_labels = [
            (self.item1_name_label, self.item1_category_label),
            (self.item2_name_label, self.item2_category_label),
            (self.item3_name_label, self.item3_category_label),
            (self.item4_name_label, self.item4_category_label),
            (self.item5_name_label, self.item5_category_label),
            (self.item6_name_label, self.item6_category_label),
        ]

        for i, (name_label, category_label) in enumerate(item_labels):
            if i < len(items):
                name_label.text = f"品項: {items[i]['name']}"
                category_label.text = f"預測內容: {items[i]['category']}"
            else:
                # 如果沒有更多品項，清空剩餘的 Label
                name_label.text = ""
                category_label.text = ""

        print("--- 發票資訊、品項和預測分類已更新 ---")


if __name__ == "__main__":
    ReceiptScannerApp().run()
