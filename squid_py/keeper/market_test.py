from unittest.mock import Mock, MagicMock

from tests.resources.tiers import unit_test
from .market import Market


@unit_test
def test_check_asset():
    contract = Mock()
    contract_concise = Mock()
    contract_concise.checkAsset = MagicMock(return_value='bla')
    contract_handler = Mock()
    contract_handler.get_concise = lambda name: contract if name == 'OceanMarket' else None
    contract_handler.get_concise_contract = lambda \
        name: contract_concise if name == 'OceanMarket' else None
    market = Market('OceanMarket', dependencies={'ContractHandler': contract_handler})
    assert market.check_asset('deadbeef') == 'bla'
    contract_concise.checkAsset.assert_called_with(b'\xde\xad\xbe\xef')
