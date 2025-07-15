# nlp_processor/main_nlp_logic.py

class NLPProcessor:
    @staticmethod
    def classify_items(items_list):
        """
        模擬 NLP 處理，將品項分類為假數據。
        """
        print(f"模擬 NLP 處理：正在分類品項: {items_list}")
        predictions = []
        # 為每個假品項生成一個假分類
        for item in items_list:
            if "蘋果汁" in item:
                predictions.append("expenses:food:drink")
            elif "肉鬆堡" in item:
                predictions.append("expenses:food:treats")
            elif "泡芙" in item:
                predictions.append("expenses:food:treats")
            else:
                predictions.append("expenses:uncategorized")
        return predictions