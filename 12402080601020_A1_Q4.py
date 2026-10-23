import csv
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Raised when a row is invalid. The message is the rejection reason."""


def validate(row):
    if len(row) != 5:
        raise ValidationError("expected 5 columns")
    tid, acc, typ, amount, ts = [c.strip() for c in row]
    if not tid or not acc:
        raise ValidationError("empty transaction_id or account_id")
    typ = typ.upper()
    if typ not in ("CREDIT", "DEBIT"):
        raise ValidationError("type must be CREDIT or DEBIT")
    try:
        amt = Decimal(amount)
    except InvalidOperation:
        raise ValidationError("amount is not numeric")
    if not amt.is_finite() or amt <= 0:
        raise ValidationError("amount must be > 0")
    try:
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValidationError("bad timestamp (yyyy-mm-ddThh:mm:ss)")
    return [tid, acc, typ, amount, ts], acc, typ, amt


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else input("CSV path: ").strip()
    balances = defaultdict(Decimal)
    try:
        with open(path, newline="", encoding="utf-8") as src, \
                open("credit.csv", "w", newline="") as fc, \
                open("debit.csv", "w", newline="") as fd, \
                open("error.csv", "w", newline="") as fe:
            reader = csv.reader(src)
            header = next(reader, None)
            if header is None:
                print("Input file is empty")
                return
            wc, wd, we = csv.writer(fc), csv.writer(fd), csv.writer(fe)
            wc.writerow(header)
            wd.writerow(header)
            we.writerow(header + ["reason"])
            for row in reader:
                if not row:
                    continue
                try:
                    clean, acc, typ, amt = validate(row)
                except ValidationError as e:     # bad row: save it and keep going
                    we.writerow(row + [str(e)])
                    continue
                if typ == "CREDIT":
                    wc.writerow(clean)
                    balances[acc] += amt
                else:
                    wd.writerow(clean)
                    balances[acc] -= amt
    except FileNotFoundError:
        print("File not found:", path)
        return
    except (OSError, csv.Error, UnicodeDecodeError) as e:
        print("Could not process file:", e)
        return
    # biggest absolute change first
    for acc, bal in sorted(balances.items(), key=lambda kv: (-abs(kv[1]), kv[0])):
        print(acc, format(bal, "f"))


if __name__ == "__main__":
    main()