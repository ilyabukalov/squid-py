from squid_py.keeper.web3_provider import Web3Provider


def test_ocean_template(publisher_ocean_instance):
    assert publisher_ocean_instance.templates.propose(
        Web3Provider.get_web3().toChecksumAddress('0x8cc84A2Cc2d9D4754Ca535C7F7e6EC5230aF6907'),
        publisher_ocean_instance.main_account)
    assert publisher_ocean_instance.templates.approve(
        Web3Provider.get_web3().toChecksumAddress('0x8cc84A2Cc2d9D4754Ca535C7F7e6EC5230aF6907'),
        publisher_ocean_instance.main_account)
    assert publisher_ocean_instance.templates.revoke(
        Web3Provider.get_web3().toChecksumAddress('0x8cc84A2Cc2d9D4754Ca535C7F7e6EC5230aF6907'),
        publisher_ocean_instance.main_account)
