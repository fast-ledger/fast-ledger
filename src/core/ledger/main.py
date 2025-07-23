import argparse
import json
from parser import manual_parse


def print_balance(journal):
    accounts = {}
    for tx in journal.transactions:
        for p in tx.postings:
            acct = p.account.name
            amt = (
                float(p.units.number) if hasattr(p, 'units') and hasattr(p.units, 'number')
                else float(p.units)    if hasattr(p, 'units')
                else float(p.amount.number) if hasattr(p, 'amount') and hasattr(p.amount, 'number')
                else float(p.amount)  if hasattr(p, 'amount')
                else 0.0
            )
            accounts[acct] = accounts.get(acct, 0) + amt
    print("Account Balance Report:")
    for acct, bal in accounts.items():
        print(f"{acct:30} {bal:.2f}")


def print_income(journal):
    income = expense = 0.0
    for tx in journal.transactions:
        for p in tx.postings:
            acct = p.account.name.lower()
            amt = (
                float(p.units.number) if hasattr(p, 'units') and hasattr(p.units, 'number')
                else float(p.units)    if hasattr(p, 'units')
                else float(p.amount.number) if hasattr(p, 'amount') and hasattr(p.amount, 'number')
                else float(p.amount)  if hasattr(p, 'amount')
                else 0.0
            )
            if acct.startswith('expenses'):
                expense += amt
            elif acct.startswith('income'):
                income += amt
    print("Income Statement Report:")
    print(f"Total Income : {income:.2f}")
    print(f"Total Expense: {expense:.2f}")
    print(f"Net Profit   : {income - expense:.2f}")


def print_cashflow(journal):
    cash_ops = []
    for tx in journal.transactions:
        for p in tx.postings:
            acct = p.account.name
            if acct == 'Assets:Cash':
                amt = (
                    float(p.units.number) if hasattr(p, 'units') and hasattr(p.units, 'number')
                    else float(p.units)    if hasattr(p, 'units')
                    else float(p.amount.number) if hasattr(p, 'amount') and hasattr(p.amount, 'number')
                    else float(p.amount)  if hasattr(p, 'amount')
                    else 0.0
                )
                cash_ops.append(amt)
    print("Cash Flow Report:")
    print(f"Operating Cash Flow: {sum(cash_ops):.2f}")


def main():
    parser = argparse.ArgumentParser(description="Ledger 報表工具")
    parser.add_argument('journal_file', help='ledger 檔案路徑')
    parser.add_argument('--balance',   action='store_true', help='資產負債表')
    parser.add_argument('--income',    action='store_true', help='損益表')
    parser.add_argument('--cashflow',  action='store_true', help='現金流量表')
    parser.add_argument('--tx',        action='store_true', help='交易明細')
    parser.add_argument('-i','--index', type=int, help='交易 index（0 開始）')
    parser.add_argument('--id',        help='receipt-number')
    parser.add_argument('--seller-id', dest='seller_id', help='seller-tax-id')
    parser.add_argument('--item',      help='只顯示含有此品名的交易')
    parser.add_argument('--receipt-time', dest='rtime', help='過濾 receipt-time (YYYY-MM-DDThh:mm:ss)')
    parser.add_argument('--date',         dest='date', help='過濾 date (YYYY-MM-DD)')
    parser.add_argument('--payee',        dest='payee', nargs='+', help='過濾 payee 名稱')
    parser.add_argument('--account',      dest='account', nargs='+', help='過濾 posting account 名稱')
    parser.add_argument('--fields',    help='逗號分隔輸出欄位: date,payee,account,quantity,amount,receipt_time,seller_tax_id')
    parser.add_argument('--items-only', action='store_true', help='僅列出每筆交易的品項名稱')
    args = parser.parse_args()

    # 合併多字參數
    if args.payee:
        args.payee = ' '.join(args.payee)
    if args.account:
        args.account = ' '.join(args.account)

    journal = manual_parse(args.journal_file)

    # 報表模式
    if args.balance:
        print_balance(journal); return
    if args.income:
        print_income(journal); return
    if args.cashflow:
        print_cashflow(journal); return

    # 交易明細
    if args.tx:
        txs = journal.transactions

        # index 過濾
        if args.index is not None:
            txs = [txs[args.index]]
        # id 過濾
        if args.id:
            txs = [t for t in txs if t.receipt.id == args.id]
        # seller-id 過濾
        if args.seller_id:
            txs = [t for t in txs if t.receipt.business.ban == args.seller_id]
        # receipt-time 過濾
        if args.rtime:
            txs = [t for t in txs if t.receipt.receipt_time.isoformat() == args.rtime]
        # date 過濾
        if args.date:
            txs = [t for t in txs if t.date.isoformat() == args.date]
        # payee 過濾
        if args.payee:
            txs = [t for t in txs if t.payee.name == args.payee]
        # account 過濾
        if args.account:
            txs = [
                t for t in txs
                if any(p.account.name == args.account for p in t.postings)
            ]
        # item 過濾
        if args.item:
            txs = [t for t in txs if any(pur.item.name == args.item for pur in t.receipt.purchases)]

        # items-only
        if args.items_only:
            for idx, t in enumerate(txs):
                print(f"Tx#{idx}: " + ", ".join(pur.item.name for pur in t.receipt.purchases))
            return

        # 準備輸出 JSON
        out = []
        for t in txs:
            rec = {
                'date': t.date.isoformat(),
                'payee': t.payee.name,
                'receipt_number': t.receipt.id,
                'receipt_time': t.receipt.receipt_time.isoformat(),
                'seller_tax_id': t.receipt.business.ban,
                'items': [
                    {'item': pur.item.name, 'quantity': int(pur.quantity), 'amount': float(pur.subtotal)}
                    for pur in t.receipt.purchases
                ],
                'postings': [
                    {'account': p.account.name, 'amount': float(p.amount)} for p in t.postings
                ]
            }
            if args.fields:
                fields = [f.strip() for f in args.fields.split(',')]
                for it in rec['items']:
                    row = {
                        'date': rec['date'],
                        'payee': rec['payee'],
                        'account': rec['postings'][0]['account'],
                        'quantity': it['quantity'],
                        'amount': it['amount'],
                        'receipt_time': rec['receipt_time'],
                        'seller_tax_id': rec['seller_tax_id'],
                    }
                    out.append({k: row[k] for k in fields if k in row})
            else:
                out.append(rec)

        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    parser.print_help()

if __name__ == '__main__':
    main()