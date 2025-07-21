from pathlib import Path
import requests
import csv


class CompanyID:

    TESTPOSTINGS_PATH = "data/BGMOPEN1.csv"
    @staticmethod
    def fetch_sheet(path=TESTPOSTINGS_PATH):

        sheetUrl = f"https://eip.fia.gov.tw/data/BGMOPEN1.csv"
        response = requests.get(sheetUrl)

        if response.status_code == 200:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"下載失敗: {response.status_code}")

    @staticmethod
    def extract_multiple_taxids(tax_id_list):
        """
        從CSV中查多筆統一編號，輸出對應欄位（第2,4,10,12,14,16）
        """
        tax_id_set = set(tax_id_list)
        target_indices = [1, 3, 9, 11, 13, 15]  # 0-based 索引
        results = []

        with open("data/BGMOPEN1.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 1 and row[1].strip() in tax_id_set:
                    extracted = []
                    for idx in target_indices:
                        val = row[idx].split(',')[0].strip() if idx < len(row) else ''
                        extracted.append(val)
                    results.append(extracted)
        print(f" {len(results)} 筆結果已讀取")
       
       
        company_info =[]
        
        for row in results:
            scopes = [scope for scope in row[2:] if scope]  # 過濾非空值
            info = {
                "business_name": row[1],
                "business_scope": scopes
            }
            company_info.append(info)

        return company_info
        
