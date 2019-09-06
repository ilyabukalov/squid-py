import logging

from ocean_keeper import Keeper
from ocean_keeper.wallet import Wallet
from ocean_keeper.web3_provider import Web3Provider


class SquidKeeper(Keeper):

    @staticmethod
    def get_instance(artifacts_path=None, contract_names=None):
        return SquidKeeper(artifacts_path)

    def get_condition_name_by_address(self, address):
        """Return the condition name for a given address."""
        if self.lock_reward_condition.address == address:
            return 'lockReward'
        elif self.access_secret_store_condition.address == address:
            return 'accessSecretStore'
        elif self.escrow_reward_condition.address == address:
            return 'escrowReward'
        else:
            logging.error(f'The current address {address} is not a condition address')

    @staticmethod
    def send_ether(from_account, to_address, ether_amount):
        w3 = Web3Provider.get_web3()
        if not w3.isChecksumAddress(to_address):
            to_address = w3.toChecksumAddress(to_address)

        tx = {
            'from': from_account.address,
            'to': to_address,
            'value': ether_amount,
            'gas': 500000}
        wallet = Wallet(w3, from_account.key_file, from_account.password, from_account.address)
        raw_tx = wallet.sign_tx(tx)
        w3.eth.sendRawTransaction(raw_tx)
