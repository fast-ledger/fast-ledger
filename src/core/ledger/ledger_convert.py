#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
import re
from collections import defaultdict
import sys

# === 0. 直接硬寫你的 Google Sheets CSV 連結 ===
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoCVtKeTg5_mEnvVT0EUPCRndBui1pd-lqeqR8UEsb1ahdHF5zJ470qvQqVji-fb-nyMxspvmHvSDF/pub?gid=2091026791&single=true&output=csv"

# === 1. 讀取試算表 ===
def load_df():
    try:
        df = pd.read_csv(CSV_URL, header=1)
    except Exception as e:
        print("讀取試算表失敗：", e, file=sys.stderr)
        sys.exit(1)

    expected = [
        '公司名稱','行業1','行業2','行業3','行業4',
        '統一編號','時間','商品品項','金額','standard zh-TW','standard en-US'
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"試算表缺少欄位: {missing}")

    cols = expected + (['receipt_no'] if 'receipt_no' in df.columns else [])
    return df[cols].copy()

# === 2. 清理並轉欄位 ===
def clean_df(df):
    rename_map = {
        '公司名稱':'merchant','行業1':'industry_1','行業2':'industry_2',
        '行業3':'industry_3','行業4':'industry_4','統一編號':'tax_id',
        '時間':'datetime','商品品項':'item','金額':'amount',
        'standard zh-TW':'account_name','standard en-US':'account_path'
    }
    df = df.rename(columns=rename_map)
    df = df[df['datetime'].astype(str) != '時間'].copy()
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df[df['datetime'].notnull()]
    return df

# === 3. Transaction 類別 ===
class Transaction:
    account_type_mapping = {
        'expenses':'Assets:Cash','income':'Income:Unknown',
        'revenue':'Income:Unknown','assets':'Assets:Bank',
        'liabilities':'Liabilities:CreditCard','equity':'Equity:Opening-Balance'
    }

    def __init__(self, dt, merchant, tax_id, note, amount, acct_path, item, receipt_no=None):
        self.datetime   = dt
        self.merchant   = merchant
        self.tax_id     = str(tax_id)
        self.note       = note
        self.amount     = float(amount)
        self.account    = str(acct_path) if pd.notna(acct_path) else ''
        self.item_desc  = item
        self.receipt_no = receipt_no or 'default_receipt'

    def extract_qty_unit(self):
        m = re.search(r"(\d+)\s*[x\*]\s*(\d+)", str(self.item_desc), re.I)
        if m:
            qty = int(m.group(1))
            unit = self.amount/qty if qty else self.amount
        else:
            qty, unit = 1, self.amount
        return qty, unit

    def to_expense_line(self):
        qty, unit = self.extract_qty_unit()
        if unit < 0:
            s = f"${unit:,.2f}"
        else:
            s = f"{qty} @ ${unit:,.2f}"
        if self.note:
            return f"    {self.account:<30}  {s}    ; {self.note}"
        return f"    {self.account:<30}  {s}"

    def get_credit_account(self):
        t = self.account.lower().split(':')[0] if ':' in self.account else self.account.lower()
        return self.account_type_mapping.get(t, 'Assets:Cash')

# === 4. 主流程：讀取 → 清理 → 轉 Transaction → 分組 → 輸出 ===
def main():
    raw = load_df()
    df = clean_df(raw)

    txns = []
    for _, r in df.iterrows():
        t = Transaction(
            dt        = r['datetime'],
            merchant  = r['merchant'],
            tax_id    = r['tax_id'],
            note      = str(r['item']),
            amount    = r['amount'],
            acct_path = r['account_path'],
            item      = r['item'],
            receipt_no= r.get('receipt_no')
        )
        txns.append(((t.receipt_no, t.datetime), t))

    grouped = defaultdict(list)
    for key, t in txns:
        grouped[key].append(t)

    with open("ledgers2.txt", 'w', encoding='utf-8') as f:
        for (rid, dt), items in grouped.items():
            f.write(f"{dt.strftime('%Y/%m/%d')} * {items[0].merchant}\n")
            total = 0
            for it in items:
                f.write(it.to_expense_line() + "\n")
                total += it.amount
            credit = items[0].get_credit_account()
            f.write(f"    {credit:<30}  ${-total:,.2f}\n")
            f.write(f"    ; receipt-time: {dt.strftime('%Y/%m/%dT%H:%M:%S')}\n")
            f.write(f"    ; seller-tax-id: {items[0].tax_id}\n")
            if rid != 'default_receipt':
                f.write(f"    ; receipt-no:: {rid}\n")
            f.write("\n")

    print("已輸出 Ledger 檔案：ledgers2.txt")

if __name__ == "__main__":
    main()