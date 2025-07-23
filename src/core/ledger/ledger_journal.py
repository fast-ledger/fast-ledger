import argparse
import json
from parser import manual_parse


def main():
    parser = argparse.ArgumentParser(description="Ledger 報表工具")
    parser.add_argument('journal_file')
    parser.add_argument('--tx', action='store_true')
    parser.add_argument('-i', '--index', type=int)
    parser.add_argument('--receipt-time', dest='rtime')
    parser.add_argument('--date', dest='date')
    parser.add_argument('--payee', dest='payee', nargs='+')
    parser.add_argument('--account', dest='account', nargs='+')
    parser.add_argument('--fields')
    args = parser.parse_args()

    if args.payee:
        args.payee = ' '.join(args.payee)
    if args.account:
        args.account = ' '.join(args.account)

    journal = manual_parse(args.journal_file)
    if not args.tx:
        parser.print_help()
        return

    txs = journal.transactions
    if args.index is not None:
        txs = [txs[args.index]]
    if args.rtime:
        txs = [t for t in txs if t.receipt.receipt_time.isoformat() == args.rtime]
    if args.date:
        txs = [t for t in txs if t.date.isoformat() == args.date]
    if args.payee:
        txs = [t for t in txs if t.payee.name == args.payee]
    if args.account:
        txs = [
            t for t in txs
            if any((p.account.name == args.account) for p in t.postings)
        ]

    out = []
    for t in txs:
        rec = {
            'date': t.date.isoformat(),
            'payee': t.payee.name,
            'receipt_time': t.receipt.receipt_time.isoformat(),
            'seller_tax_id': t.receipt.business.ban,
            'items': [
                {'item': p.item.name, 'quantity': int(p.quantity), 'amount': float(p.subtotal)}
                for p in t.receipt.purchases
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

if __name__ == '__main__':
    main()