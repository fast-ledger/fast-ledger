# ocr_processor/main_ocr_logic.py


class OCRProcessor:
    @staticmethod
    def process_camera_texture(texture):
        """
        模擬 OCR 處理，返回假數據。
        """
        print("模擬 OCR 處理：從攝像頭紋理獲取假發票數據。")
        # 返回一個模擬的字典，結構與 main.py 中期望的相符
        return {
            "invoice_number": "FM12345678",
            "buyer_identifier": "00000000",
            "seller_identifier": "91601740",
            "time": "2025/07/07 15:18",
            "business_name": "歐立食品股份有限公司南勢角門市部",
            "industry": "未分類其他食品、飲料及菸草製品零售",
            "industry_sub": "咖啡館",
            "items": [
                {"name": "玻璃-樹頂蘋果汁300ml"},
                {"name": "肉鬆堡"},
                {"name": "脆皮泡芙(草莓)"},
            ],
        }

    @staticmethod
    def process_image_path(image_path):
        """
        模擬 OCR 處理，從圖片路徑獲取假數據。
        （此方法在 main.py 中未直接使用，但作為模組的完整性）
        """
        print(f"模擬 OCR 處理：從 {image_path} 獲取假發票數據。")
        return OCRProcessor.process_camera_texture(None)  # 直接返回相同的假數據
