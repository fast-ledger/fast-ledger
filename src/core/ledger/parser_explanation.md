# Ledger Parser Module - Detailed Explanation

## 1. Overall Architecture

```
┌─────────────┐      ┌────────────────┐     ┌──────────────────────┐
│ main.py     │ ───► │ run_ledger_json│ ───►│ parse_json_to_models │
└─────────────┘      └────────────────┘     └──────────────────────┘
       │                      │                       │
       ▼                      ▼                       ▼
┌─────────────┐             ┌─────────────────┐   ┌────────────────┐
│ manual_parse│◄─ fallback ─┤ Ledger CLI JSON ├──►│ Journal Model  │
└─────────────┘             └─────────────────┘   └────────────────┘
                                     │
                                     ▼
                               ┌────────────┐
                               │ serialize  │
                               └────────────┘
                                     │
                                     ▼
                          Text Ledger Format Output
```

- **main.py / ledger_journal.py / extract.py / report.py** call `run_ledger_json()`.
- **run_ledger_json()** tries JSON parsing via `ledger-cli --json`; on failure, uses `manual_parse()`.
- **manual_parse()** reads raw file line by line, regex-driven extraction into data classes.
- **parse_json_to_models()** converts ledger-cli JSON to data classes.
- **serialize_transactions_to_ledger()** reassembles data classes back into text format.

## 2. Detailed Parsing Steps

### manual_parse()

1. **Read File**  
   - UTF-8 with replacement to avoid errors.
2. **Scan Lines**  
   - Identify transaction header: `YYYY/MM/DD * payee`.
3. **Metadata, Postings, Purchases**  
   - Lines starting with 4 spaces:
     - `; key: value` → metadata
     - `qty @ $price ; description` → purchases + postings(Account("UNKNOWN"))
     - other lines → postings(account, amount)
4. **Business / Payee**  
   - From metadata keys `seller-tax-id`, `business-scope`.
5. **Receipt**  
   - Assemble `Receipt(id, datetime, purchases, remaining metadata)`
6. **Transaction**  
   - Combine `date, payee, postings, receipt` into `Transaction`.
7. **Journal**  
   - Append each transaction to `Journal.transactions`.

### run_ledger_json()

1. **Fetch content CP950** → write TMP UTF-8.
2. **Subprocess**: `ledger --json -f tmp print`.
3. **If valid JSON**: `parse_json_to_models()`.
4. **Else**: fallback to `manual_parse()`.

### parse_json_to_models()

- Map accounts.
- For each transaction:
  - Extract date, payee, tags.
  - Build postings & purchases (same regex).
  - Build Receipt and Transaction.

### serialize_transactions_to_ledger()

- For each Transaction:
  - Header: `YYYY-MM-DD * payee`.
  - Indented postings.
  - Indented metadata lines.
  - Blank line.

## 3. Regular Expression Breakdown

```regex
^\d{4}/\d{2}/\d{2}
```
- Matches transaction header date at line start.

```python
m = re.search(r"(\d+)\s*@\s*\$(\d+(?:\.\d+)?)", left)
```
- **(\d+)**: one or more digits → quantity  
- **\s*@\s***: '@' with optional spaces around  
- **\$(\d+(?:\.\d+)?)**: '$' followed by integer or decimal

```python
raw.startswith(";")
```
- Lines beginning with ';' are metadata.

```python
lines[idx].startswith("    ")
```
- Exactly four spaces → indentation for transaction body.

## 4. Error Handling & Fallback Flow

```
                            ┌────────────────────┐
                            │ run_ledger_json()  │
                            └────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                │                                           │
        JSON parse OK?                                    JSON parse Error
                │                                           │
                ▼                                           ▼
┌──────────────────────────────┐                   ┌────────────────────────┐
│ parse_json_to_models(data)   │                   │ manual_parse(path)     │
└──────────────────────────────┘                   └────────────────────────┘
                │                                           │
                └─────────────────────┬─────────────────────┘
                                      ▼
                            ┌────────────────────┐
                            │ return Journal     │
                            └────────────────────┘
```

---

_End of Explanation_
