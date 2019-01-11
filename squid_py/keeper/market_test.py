from unittest.mock import Mock, MagicMock
from tests.resources.tiers import unit_test
from .market import Market

@unit_test
def test_check_asset():
    contract = Mock()
    contract_consise = Mock()
    contract_consise.checkAsset = MagicMock(return_value='bla')
    ContractHandler = Mock()
    ContractHandler.get_concise = lambda name: contract if name == 'OceanMarket' else None
    ContractHandler.get_concise_contract = lambda name: contract_consise if name == 'OceanMarket' else None
    market = Market('OceanMarket', dependencies={'ContractHandler': ContractHandler})
    assert market.check_asset('deadbeef') == 'bla'
    contract_consise.checkAsset.assert_called_with(b'\xde\xad\xbe\xef')
