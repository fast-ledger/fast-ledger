from pathlib import Path
import requests
import csv


class CompanyID:

    BUSINESS_INFO_PATH = "data/BGMOPEN1.csv"
    @staticmethod
    def fetch_business_info(path=BUSINESS_INFO_PATH):
        FETCH_PATH = "https://eip.fia.gov.tw/data/BGMOPEN1.csv"

        print(f"Fetching data from {FETCH_PATH}")
        response = requests.get(FETCH_PATH)

        if response.status_code == 200:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as file:
                file.write(response.content)
        else:
            print(f"下載失敗: {response.status_code}")

    @staticmethod
    def ban_lookups(ban_list):
        """
        從CSV中查多筆統一編號，輸出對應欄位（第2,4,10,12,14,16）
        """
        if not Path(CompanyID.BUSINESS_INFO_PATH).is_file():
            CompanyID.fetch_business_info()
        
        target_indices = [1, 3, 9, 11, 13, 15]  # 0-based 索引
        results = [None] * len(ban_list)

        with open("data/BGMOPEN1.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) > 1 and row[1].strip() in ban_list:
                    extracted = []
                    for idx in target_indices:
                        val = row[idx].split(',')[0].strip() if idx < len(row) else ''
                        extracted.append(val)
                    # Insert row in given ban order
                    results[ban_list.index(row[1])] = extracted
        print(f" {len(results)} 筆結果已讀取")
       
        company_info = []
        for row in results:
            if row == None:
                company_info.append(None)
                continue

            scopes = [scope for scope in row[2:] if scope]  # 過濾非空值
            info = {
                "business_name": row[1],
                "business_scope": scopes
            }
            company_info.append(info)

        return company_info
        
    @staticmethod
    def ban_lookup(ban):
        return CompanyID.ban_lookups([ban])[0]
