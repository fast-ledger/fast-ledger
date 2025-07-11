from pathlib import Path
import requests
import pandas as pd

GOOGLESHEET_ID = "1dHxFMzxJzud7SlQeZYBuFMXsYjz1RBmiX-rZc4SubQ4"
TESTPOSTINGS_PATH = "data/test-postings.csv"

def fetchGoogleSheet(id=GOOGLESHEET_ID, path=TESTPOSTINGS_PATH):
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

def postings(path=TESTPOSTINGS_PATH, force=False):
    file = Path(path)

    if force or not file.exists():
        fetchGoogleSheet()

    return pd.read_csv(path)

if __name__ == "__main__":
    postings(force=True)