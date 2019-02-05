
class OceanTokens:
    def __init__(self, keeper):
        self._keeper = keeper

    def request(self, account, amount):
        self._keeper.unlock_account(account)
        return self._keeper.dispenser.request_tokens(amount, account.address)

    def transfer(self, receiver_address, amount, sender_account):
        self._keeper.unlock_account(sender_account)
        self._keeper.token.token_approve(receiver_address, amount,
                                         sender_account)
        self._keeper.token.transfer(receiver_address, amount, sender_account)
