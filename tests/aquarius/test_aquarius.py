import pytest

from squid_py.aquarius.aquarius import Aquarius
from squid_py.ocean.asset import Asset
from tests.resources.helper_functions import get_resource_path

aquarius = Aquarius()
sample_ddo_path1 = get_resource_path('ddo', 'ddo_sample1.json')
assert sample_ddo_path1.exists(), "{} does not exist!".format(sample_ddo_path1)
asset1 = Asset.from_ddo_json_file(sample_ddo_path1)
sample_ddo_path2 = get_resource_path('ddo', 'ddo_sample2.json')
assert sample_ddo_path1.exists(), "{} does not exist!".format(sample_ddo_path1)
asset2 = Asset.from_ddo_json_file(sample_ddo_path2)


def test_get_service_endpoint():
    assert aquarius.get_service_endpoint('did:op:test') == f'{aquarius.url}did:op:test'


def test_publish_valid_ddo():
    aquarius.publish_asset_ddo(asset1.ddo)
    assert aquarius.get_asset_ddo(asset1.did)
    aquarius.retire_asset_ddo(asset1.did)


def test_publish_invalid_ddo():
    with pytest.raises(AttributeError):
        aquarius.publish_asset_ddo({})


def test_publish_ddo_already_registered():
    aquarius.publish_asset_ddo(asset1.ddo)
    with pytest.raises(ValueError):
        aquarius.publish_asset_ddo(asset1.ddo)
    aquarius.retire_asset_ddo(asset1.did)


def test_get_asset_ddo_for_not_registered_did():
    invalid_did = 'did:op:not_valid'
    with pytest.raises(ValueError):
        aquarius.get_asset_ddo(invalid_did)


def test_get_asset_metadata():
    aquarius.publish_asset_ddo(asset1.ddo)
    metadata_dict = aquarius.get_asset_metadata(asset1.did)
    assert isinstance(metadata_dict, dict)
    assert 'base' in metadata_dict
    assert 'curation' in metadata_dict
    assert 'additionalInformation' in metadata_dict
    aquarius.retire_asset_ddo(asset1.did)


def test_get_asset_metadata_for_not_registered_did():
    invalid_did = 'did:op:not_valid'
    with pytest.raises(ValueError):
        aquarius.get_asset_metadata(invalid_did)


def test_list_assets():
    assert len(aquarius.list_assets()) == 0
    aquarius.publish_asset_ddo(asset1.ddo)
    assert len(aquarius.list_assets()) == 1
    assert isinstance(aquarius.list_assets(), list)
    assert isinstance(aquarius.list_assets()[0], str)
    aquarius.retire_asset_ddo(asset1.did)


def test_list_assets_ddo():
    assert len(aquarius.list_assets_ddo()) == 0
    aquarius.publish_asset_ddo(asset1.ddo)
    assert len(aquarius.list_assets_ddo()) == 1
    assert isinstance(aquarius.list_assets_ddo(), dict)
    aquarius.retire_asset_ddo(asset1.did)


def test_update_ddo():
    aquarius.publish_asset_ddo(asset1.ddo)
    aquarius.update_asset_ddo(asset1.did, asset2.ddo)
    assert aquarius.get_asset_ddo(asset1.did)['id'] == asset2.did
    aquarius.retire_asset_ddo(asset1.did)


def test_update_with_not_valid_ddo():
    with pytest.raises(Exception):
        aquarius.update_asset_ddo(asset1.did, {})


def test_text_search():
    num_matches = len(aquarius.text_search(text='Office'))
    aquarius.publish_asset_ddo(asset1.ddo)
    assert len(aquarius.text_search(text='Office')) == (num_matches + 1)
    aquarius.publish_asset_ddo(asset2.ddo)
    assert len(aquarius.text_search(
        text='d75305ebc1617834339e64cdafb7fd542aa657c0f94dac0f4f84068f5f910ca2')) == (
                   num_matches + 1)
    assert len(aquarius.text_search(text='Office')) == (num_matches + 2)
    aquarius.retire_asset_ddo(asset1.did)
    aquarius.retire_asset_ddo(asset2.did)


def test_text_search_invalid_query():
    with pytest.raises(Exception):
        aquarius.text_search(text='', offset='Invalid')


def test_query_search():
    num_matches = len(
        aquarius.query_search(search_query={"query": {}}))
    aquarius.publish_asset_ddo(asset1.ddo)
    assert len(aquarius.query_search(search_query={"query": {}})) == (num_matches + 1)
    aquarius.publish_asset_ddo(asset2.ddo)
    assert len(aquarius.query_search(search_query={"query": {}})) == (num_matches + 2)
    assert len(aquarius.query_search(
        search_query={"query": {"service.metadata.base.name": "UK Weather information 2011"}})) == (
                   num_matches + 1)
    assert len(aquarius.query_search(
        search_query={"query": {"service.metadata.base.name": "UK Weather information 2012"}})) == (
                   num_matches + 1)
    aquarius.retire_asset_ddo(asset1.did)
    aquarius.retire_asset_ddo(asset2.did)


def test_query_search_invalid_query():
    with pytest.raises(Exception):
        aquarius.query_search(search_query='')


def test_retire_ddo():
    aquarius.publish_asset_ddo(asset1.ddo)
    assert len(aquarius.list_assets()) == 1
    aquarius.retire_asset_ddo(asset1.did)
    assert len(aquarius.list_assets()) == 0


def test_retire_not_published_did():
    with pytest.raises(Exception):
        aquarius.retire_asset_ddo('did:op:not_registered')
