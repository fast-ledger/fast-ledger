from decimal import Decimal
from typing import Dict
from ledger_journal import LedgerJournal


def report_balance(journal: LedgerJournal) -> None:
    balances: Dict[str, Decimal] = {}
    for idx, txn in enumerate(journal.transactions, 1):
        print(f"DEBUG: Transaction #{idx}: date={txn.date}, postings={len(txn.postings)}")
        for p in txn.postings:
            print(f"  -> {p.account.name}: {p.amount}")
            balances[p.account.name] = balances.get(p.account.name, Decimal('0')) + p.amount

    print("Account Balance Report:")
    for acct in sorted(balances):
        print(f"{acct:<40} {balances[acct]:>12}")


def report_cashflow(journal: LedgerJournal) -> None:
    # 範例現金流量表：只列出現金相關帳戶交易
    cash_accounts = [acct for acct in journal.accounts if 'Cash' in acct.name]
    cash_set = set(acct.name for acct in cash_accounts)
    flows: Dict[str, Decimal] = {}
    for txn in journal.transactions:
        for posting in txn.postings:
            acct_name = posting.account.name
            if acct_name in cash_set:
                key = txn.date.isoformat()
                flows[key] = flows.get(key, Decimal('0')) + posting.amount

    print("Cash Flow Report:")
    for date in sorted(flows):
        print(f"{date} {flows[date]:>12}")


def report_income(journal: LedgerJournal) -> None:
    # 範例損益表：彙總收入與支出
    income: Decimal = Decimal('0')
    expense: Decimal = Decimal('0')
    for txn in journal.transactions:
        for posting in txn.postings:
            acct_name = posting.account.name.lower()
            if acct_name.startswith('income'):
                income += posting.amount
            if acct_name.startswith('expenses'):
                expense += posting.amount

    profit = income + expense
    print("Income Statement Report:")
    print(f"Total Income : {income:>12}")
    print(f"Total Expense: {expense:>12}")
    print(f"Net Profit   : {profit:>12}")