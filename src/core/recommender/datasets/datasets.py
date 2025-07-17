from pathlib import Path
import requests
import pandas as pd

GOOGLESHEET_ID = "1dHxFMzxJzud7SlQeZYBuFMXsYjz1RBmiX-rZc4SubQ4"
TESTPOSTINGS_PATH = "data/test-postings.csv"

def fetch_google_sheet(id=GOOGLESHEET_ID, path=TESTPOSTINGS_PATH):
    """
    抓取 Google Drive 上的測試帳本至本地
    """
    sheetUrl = f"https://docs.google.com/spreadsheets/d/{id}/export?format=csv"
    response = requests.get(sheetUrl)

    if response.status_code == 200:
        print("Test journal downloaded")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as file:
            file.write(
                response.content[response.content.find(b'\n') + 1:]  # Remove first row
            )

class Dataset:
    def __init__(self, path=TESTPOSTINGS_PATH, force=False):
        file = Path(path)

        if force or not file.exists():
            fetch_google_sheet()

        self.frame = pd.read_csv(path).rename(columns={
            "公司名稱": "business_name",
            "行業1": "scope_1",
            "行業2": "scope_2",
            "行業3": "scope_3",
            "行業4": "scope_4",
            "統一編號": "ban",
            "時間": "datetime",
            "商品品項": "item",
            "金額": "subtotal",
        })
    
    def subset(self, subset_name):
        match subset_name:
            case "lunch-dinner":
                return self.frame[
                    self.frame['ljavuras'].str.contains("expenses:food:dining:")
                ].reset_index()

def fetch_dataset(path=TESTPOSTINGS_PATH, force=False):
    return Dataset(path=path, force=force)

if __name__ == "__main__":
    fetch_google_sheet()