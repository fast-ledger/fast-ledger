import re
from datetime import datetime
from decimal import Decimal
from dateutil import parser as date_parser

from models import (
    Journal,
    Account,
    Business,
    Payee,
    Item,
    Purchase,
    Receipt,
    Posting,
    Transaction,
)


def manual_parse(path: str) -> Journal:
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    journal = Journal([], [], [])
    idx = 0

    while idx < len(lines):
        line = lines[idx].strip()
        if re.match(r"^\d{4}/\d{2}/\d{2}", line):
            date_str, _, payee_name = line.partition("*")
            tx_date = datetime.strptime(date_str.strip(), "%Y/%m/%d").date()

            postings = []  # type: List[Posting]
            purchases = []  # type: List[Purchase]
            metadata = {}

            idx += 1
            while idx < len(lines) and lines[idx].startswith("    "):
                raw = lines[idx].lstrip()

                # metadata line
                if raw.startswith(";"):
                    k, _, v = raw.lstrip(";").partition(":")
                    metadata[k.strip()] = v.strip()

                # purchase line: account qty @ price ; description
                elif "@" in raw and ";" in raw:
                    # split off comment for item description
                    left, comment = raw.split(";", 1)
                    desc = comment.strip()

                    # extract account, quantity, price
                    parts = left.strip().split()
                    # account name is all up to the quantity
                    # find index of quantity
                    qty_idx = next(i for i, tok in enumerate(parts) if tok.isdigit())
                    acct_name = " ".join(parts[:qty_idx])
                    qty = Decimal(parts[qty_idx])
                    # price after '@'
                    price = Decimal(parts[qty_idx + 2].lstrip("$"))

                    # create postings and purchases
                    postings.append(Posting(account=Account(name=acct_name), commodity=None, amount=qty * price))
                    purchases.append(Purchase(item=Item(name=desc), quantity=qty, subtotal=qty * price))

                # other posting lines: account amount
                else:
                    parts = raw.split()
                    if len(parts) >= 2:
                        amt = Decimal(parts[-1].replace("$", ""))
                        acct_name = " ".join(parts[:-1])
                        postings.append(Posting(account=Account(name=acct_name), commodity=None, amount=amt))

                idx += 1

            # build business and payee
            ban = metadata.get("seller-tax-id", metadata.get("ban", ""))
            biz = Business(
                business_name=payee_name.strip(),
                use_parent_name=False,
                ban=ban,
                business_scope=[],
                parent_business=None,
                metadata=metadata,
            )
            payee = Payee(name=payee_name.strip(), business=biz)

            # build receipt and transaction
            receipt = Receipt(
                id=metadata.get("receipt-number", ""),
                datetime=(date_parser.parse(metadata["receipt-time"]) if "receipt-time" in metadata else tx_date),
                business=biz,
                purchases=purchases,
                metadata=metadata,
            )
            tx = Transaction(date=tx_date, payee=payee, postings=postings, receipt=receipt)
            journal.transactions.append(tx)
        else:
            idx += 1

    return journal