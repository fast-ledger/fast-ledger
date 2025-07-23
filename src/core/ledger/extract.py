import sys, json, argparse, io, contextlib
from datetime import datetime
from parser import manual_parse

# 先 suppress 那個 ledger-cli warning
_real_stdout = sys.stdout
_suppress = io.StringIO()
with contextlib.redirect_stdout(_suppress):
    from ledger_journal import LedgerJournal
    j = LedgerJournal.load('test1.ledger')
sys.stdout = _real_stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 參數
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--index', type=int)
args = parser.parse_args()

def serialize_tx(tx):
    rows = []
    for p in tx.receipt.purchases:
        rows.append({
            'date':           tx.date.isoformat(),
            'payee':          tx.payee.name,
            'receipt_number': tx.receipt.id,
            'receipt_time':   tx.receipt.datetime.isoformat() if tx.receipt.datetime else '',
            'seller_tax_id':  tx.receipt.business.ban,
            'item':           p.item.name,
            'quantity':       int(p.quantity),
            'amount':         float(p.subtotal),
        })
    return rows

if args.index is None:
    out = sum((serialize_tx(tx) for tx in j.transactions), [])
else:
    out = serialize_tx(j.transactions[args.index])

#  **這裡改成 ensure_ascii=True，強制 escape 所有非 ASCII**
print(json.dumps(out, ensure_ascii=True))