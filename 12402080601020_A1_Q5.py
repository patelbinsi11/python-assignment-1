import sys


class BankError(Exception):
    pass


class InsufficientFundsError(BankError):
    pass


class AccountNotFoundError(BankError):
    pass


class InvalidAmountError(BankError):
    pass


class Transaction:
    def __init__(self, kind, src, dst, amount):
        self.kind, self.src, self.dst, self.amount = kind, src, dst, amount


class Account:
    def __init__(self, acc_id, balance):
        self._id = acc_id
        self._balance = balance

    @property
    def acc_id(self):
        return self._id

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:                       # overdraft is not allowed
            raise InsufficientFundsError(f"{self._id}: overdraft not allowed")
        self._balance = value


class Bank:
    def __init__(self):
        self._accounts = {}
        self.history = []
        self._snapshot = None               # original balances during a batch
        self._hist_len = 0

    def add_account(self, acc_id, balance):
        self._accounts[acc_id] = Account(acc_id, balance)

    def _get(self, acc_id):
        try:
            acc = self._accounts[acc_id]
        except KeyError:
            raise AccountNotFoundError(acc_id)
        if self._snapshot is not None:      # remember balance before first change
            self._snapshot.setdefault(acc_id, acc.balance)
        return acc

    @staticmethod
    def _check(amount):
        if amount <= 0 or amount > 10 ** 9:
            raise InvalidAmountError(str(amount))

    def deposit(self, acc, amount):
        self._check(amount)
        a = self._get(acc)
        a.balance = a.balance + amount
        self.history.append(Transaction("DEPOSIT", None, acc, amount))

    def withdraw(self, acc, amount):
        self._check(amount)
        a = self._get(acc)
        a.balance = a.balance - amount
        self.history.append(Transaction("WITHDRAW", acc, None, amount))

    def transfer(self, src, dst, amount):
        self._check(amount)
        a, b = self._get(src), self._get(dst)
        a.balance = a.balance - amount
        b.balance = b.balance + amount
        self.history.append(Transaction("TRANSFER", src, dst, amount))

    def begin_batch(self):
        self._snapshot, self._hist_len = {}, len(self.history)

    def commit(self):
        self._snapshot = None

    def rollback(self):
        for acc_id, bal in self._snapshot.items():
            self._accounts[acc_id]._balance = bal
        del self.history[self._hist_len:]
        self._snapshot = None

    def balances(self):
        return sorted((a.acc_id, a.balance) for a in self._accounts.values())


def main():
    tokens = [ln.split() for ln in sys.stdin.read().split("\n") if ln.strip()]
    bank, failed, batch_no = Bank(), [], 0
    try:
        n = int(tokens[0][0])
        for t in tokens[1:1 + n]:
            bank.add_account(t[0], int(t[1]))
        q = int(tokens[1 + n][0])
        ops = tokens[2 + n: 2 + n + q]
    except (IndexError, ValueError):
        print("Input error")
        return
    in_batch = batch_failed = False
    for op in ops:
        cmd = op[0].upper()
        if cmd == "BATCH_BEGIN":
            batch_no += 1
            in_batch, batch_failed = True, False
            bank.begin_batch()
            continue
        if cmd == "BATCH_END":
            if in_batch:
                if batch_failed:
                    bank.rollback()
                    failed.append(batch_no)
                else:
                    bank.commit()
            in_batch = False
            continue
        if in_batch and batch_failed:
            continue                        # this batch already failed
        try:
            if cmd == "DEPOSIT":
                bank.deposit(op[1], int(op[2]))
            elif cmd == "WITHDRAW":
                bank.withdraw(op[1], int(op[2]))
            elif cmd == "TRANSFER":
                bank.transfer(op[1], op[2], int(op[3]))
            else:
                raise BankError("unknown operation " + cmd)
        except (BankError, IndexError, ValueError) as e:
            if in_batch:
                batch_failed = True
            else:
                print("Rejected:", " ".join(op), "->", e, file=sys.stderr)
    if in_batch:                            # BATCH_END missing
        bank.rollback()
        failed.append(batch_no)
    for b in failed:
        print("FAILED", b)
    for acc_id, bal in bank.balances():
        print(acc_id, bal)


if __name__ == "__main__":
    main()