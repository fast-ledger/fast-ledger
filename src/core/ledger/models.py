from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional

@dataclass
class Account:
    name: str
    display_name: Optional[str] = None

@dataclass
class Business:
    business_name: str
    use_parent_name: bool = False
    ban: str = ""
    business_scope: List[str] = field(default_factory=list)
    parent_business: Optional['Business'] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def get_name(self) -> str:
        if self.use_parent_name and self.parent_business:
            return self.parent_business.get_name
        return self.business_name

@dataclass
class Payee:
    name: str
    business: Business

@dataclass
class Item:
    name: str

@dataclass
class Purchase:
    item: Item
    quantity: int
    subtotal: Decimal
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class Receipt:
    id: str
    datetime: datetime
    business: Business
    purchases: List[Purchase]
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def receipt_number(self) -> str:
        return self.metadata.get("receipt-number", "")

    @property
    def receipt_time(self) -> datetime:
        raw = self.metadata.get("receipt-time", "")
        if raw:
            try:
                return datetime.fromisoformat(raw)
            except ValueError:
                return self.datetime
        return self.datetime

    @property
    def seller_tax_id(self) -> str:
        raw = self.metadata.get("seller-tax-id", "")
        return raw.strip("[]")

@dataclass
class Posting:
    account: Account
    commodity: Optional[str]
    amount: Decimal

@dataclass
class Transaction:
    date: date
    payee: Payee
    postings: List[Posting]
    receipt: Receipt
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class Journal:
    payees: List[Payee]
    accounts: List[Account]
    transactions: List[Transaction]

    def get_transactions(self, **filters) -> List[Transaction]:
        result = self.transactions
        if 'payee_name' in filters:
            result = [tx for tx in result if tx.payee.name == filters['payee_name']]
        if 'account_name' in filters:
            result = [tx for tx in result
                      if any(p.account.name == filters['account_name'] for p in tx.postings)]
        if 'item_name' in filters:
            result = [tx for tx in result
                      if any(pu.item.name == filters['item_name'] for pu in tx.receipt.purchases)]
        return result

    def new_transaction(self, tx: Transaction) -> None:
        self.transactions.append(tx)

    def save_to_file(self, path: str) -> None:
        from parser import serialize_transactions_to_ledger
        content = serialize_transactions_to_ledger(self.transactions)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)