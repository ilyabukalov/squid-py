from squid_py.config import Config
from squid_py.ocean.asset import Asset
from squid_py.ocean.ocean import Ocean
from squid_py.ddo import DDO
import pathlib
import json


def test_aquarius():
    ocean_provider = Ocean(Config('config_local.ini'))
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample1.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    asset1 = Asset.from_ddo_json_file(sample_ddo_path)

    #    print(asset1.ddo.as_text())
    # Ensure the asset it not already in database
    ocean_provider.metadata_store.retire_asset_ddo(asset1.did)

    # Ensure there are no matching assets before publishing
    for match in ocean_provider.metadata_store.text_search(text='Office'):
        ocean_provider.metadata_store.retire_asset_ddo(match['id'])

    num_assets = len(ocean_provider.metadata_store.list_assets())
    ddo = ocean_provider.metadata_store.publish_asset_ddo(asset1.ddo)

    ddo = ocean_provider.metadata_store.get_asset_ddo(asset1.did)

    assert len(ocean_provider.metadata_store.text_search(text='Office')) == 1

    sample_ddo_path2 = pathlib.Path.cwd() / 'tests' / 'resources' / 'ddo' / 'ddo_sample2.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)
    assert len(ocean_provider.metadata_store.list_assets()) == (num_assets + 1)
    asset2 = Asset.from_ddo_json_file(sample_ddo_path2)

    ocean_provider.metadata_store.update_asset_ddo(asset2.did, asset2.ddo)
    ddo = ocean_provider.metadata_store.get_asset_ddo(asset2.did)
    metadata = ocean_provider.metadata_store.get_asset_metadata(asset2.did)

    # basic test to compare authentication records in the DDO
    ddo = DDO(json_text=json.dumps(ddo))
    assert ddo.authentications[0].as_text() == asset2.ddo.authentications[0].as_text()
    assert 'base' in metadata

    ocean_provider.metadata_store.retire_asset_ddo(asset2.did)
