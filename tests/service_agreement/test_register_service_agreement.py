import unittest
import uuid

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_contract_by_name, get_fingerprint_by_name, hexstr_to_bytes
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.utils.web3_helper import Web3Helper


CONFIG_PATH = 'config_local.ini'


class TestRegisterServiceAgreement(unittest.TestCase):

    def setUp(self):
        self.config = Config(CONFIG_PATH)
        self.web3 = Web3(HTTPProvider(self.config.keeper_url))
        self.web3helper = Web3Helper(self.web3)

        self._setup_service_agreement()
        self._setup_token()

    def test_register_service_agreement_subscribes_to_events(self):
        service_agreement_id = uuid.uuid4().hex

        register_service_agreement(
            self.web3helper,
            self.config,
            service_agreement_id,
            {
                'conditions': [{
                    'condition_key': {
                        'contract_address': self.payment_contract.address
                    },
                    'events': [{
                        'name': 'PaymentLocked',
                        'actor_type': 'consumer',
                        'handler': {
                            'module_name': 'payment',
                            'function_name': 'lockPayment',
                            'version': '0.1'
                        }
                    }]
                }]
            }
        )

        did = uuid.uuid4().hex
        price = 10
        self._execute_service_agreement(service_agreement_id, did, price)
        self._lock_payment(service_agreement_id, did, price)

        while True:
            import time
            time.sleep(0.5)

    def _setup_service_agreement(self):
        self.consumer = self.web3.eth.accounts[0]
        self.web3.eth.defaultAccount = self.consumer

        contract = get_contract_by_name(self.config, self.web3helper.network_name,
                                        'ServiceAgreement')
        self.service_agreement = self.web3.eth.contract(address=contract['address'],
                                                        abi=contract['abi'])

        payment_contract = get_contract_by_name(self.config, self.web3helper.network_name,
                                                'PaymentConditions')
        self.payment_contract = self.web3.eth.contract(address=payment_contract['address'],
                                                       abi=payment_contract['abi'])

        self.contracts = [payment_contract['address']]
        self.fingerprints = [
            hexstr_to_bytes(self.web3,
                            get_fingerprint_by_name(payment_contract['abi'], 'lockPayment'))
        ]
        self.dependencies = [0]

        template_name = uuid.uuid4().hex.encode()
        setup_args = [self.contracts, self.fingerprints, self.dependencies, template_name]
        receipt = self.service_agreement.functions.setupAgreementTemplate(*setup_args).transact()
        tx = self.web3.eth.waitForTransactionReceipt(receipt)

        self.template_id = Web3.toHex(self.service_agreement.events.
                                      SetupAgreementTemplate().processReceipt(tx)[0].args.
                                      serviceTemplateId)

    def _execute_service_agreement(self, service_agreement_id, did, price):
        hashes = [
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did.encode(), price]
            ).hex()
        ]
        condition_keys = [
            self.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [hexstr_to_bytes(self.web3, self.template_id),
                 self.contracts[0],
                 self.fingerprints[0]]
            ).hex()
        ]
        timeouts = [0]
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [hexstr_to_bytes(self.web3, self.template_id),
                 condition_keys,
                 hashes,
                 timeouts,
                 service_agreement_id.encode()]
            ).hex()
        ).hex()

        execute_args = [
            hexstr_to_bytes(self.web3, self.template_id),
            signature,
            self.consumer,
            hashes,
            timeouts,
            service_agreement_id.encode(),
            did.encode(),
        ]
        receipt = self.service_agreement.functions.executeAgreement(*execute_args).transact()
        tx = self.web3.eth.waitForTransactionReceipt(receipt)

    def _setup_token(self):
        market = get_contract_by_name(self.config, self.web3helper.network_name, 'OceanMarket')
        market = self.web3.eth.contract(address=market['address'], abi = market['abi'])

        market.functions.requestTokens(100).transact()

        token = get_contract_by_name(self.config, self.web3helper.network_name, 'OceanToken')
        token = self.web3.eth.contract(address=token['address'], abi=token['abi'])

        token.functions.approve(self.payment_contract.address, 100).transact()

    def _lock_payment(self, service_agreement_id, did, price):
        receipt = self.payment_contract.functions.lockPayment(
            service_agreement_id.encode(),
            did.encode(),
            price
        ).transact()
        tx = self.web3.eth.waitForTransactionReceipt(receipt)
        print(self.payment_contract.events.PaymentLocked().processReceipt(tx))

