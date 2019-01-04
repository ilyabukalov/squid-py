"""Ocean module."""

import logging

from squid_py.ddo import DDO
from squid_py.did import did_to_id
from squid_py.ocean.ocean_base import OceanBase
from squid_py.service_agreement.service_types import ServiceTypes

DDO_SERVICE_METADATA_KEY = 'metadata'

logger = logging.getLogger('asset')


class Asset(OceanBase):
    """Class representing and asset."""

    def __init__(self, ddo, publisher_id=None):
        """
        Represent an asset in the MetaData store.

        Constructor methods:
            1. Direct instantiation Asset(**kwargs)
                - Use this method to manually build an asset
            2. From a json DDO file Asset.from_ddo_json_file()
                - Create an asset based on a DDO file

        :param publisher_id:
        :param ddo: DDO instance
        """
        assert ddo and isinstance(ddo, DDO), 'Must provide a valid DDO instance.'
        self._ddo = ddo
        self.publisher_id = publisher_id
        self.asset_id = did_to_id(self._ddo.did)
        OceanBase.__init__(self, self.asset_id)

    def __str__(self):
        return f'Asset {self.did}, publisher: {self.publisher_id}'

    def get_id(self):
        return self.id

    @property
    def did(self):
        """
        Return the DID for this asset.

        :return: DID
        """
        if not self._ddo:
            raise AttributeError(f'No DDO object in {self}')
        if not self._ddo.is_valid:
            raise ValueError(f'Invalid DDO object in {self}')

        return self._ddo.did

    @property
    def ddo(self):
        """
        Return ddo object assigned for this asset.

        :return: DDO
        """
        return self._ddo

    @classmethod
    def from_ddo_json_file(cls, json_file_path):
        """
        Return a new Asset from a json file with a ddo.

        :param json_file_path: Json file path, str
        :return: Asset
        """
        asset = cls(DDO(json_filename=json_file_path))
        logging.debug(f'Asset {asset.did} created from ddo file {json_file_path}.')
        return asset

    @classmethod
    def from_ddo_dict(cls, dictionary):
        """
        Return a new Asset object from DDO dictionary.

        :param dictionary: dict
        :return: Asset
        """
        asset = cls(ddo=DDO(dictionary=dictionary))
        logger.debug(f'Asset {asset.asset_id} created from ddo dict {dictionary}.')
        return asset

    @property
    def metadata(self):
        """Asset metadata object."""
        assert self.has_metadata
        return self._get_metadata()

    @property
    def has_metadata(self):
        """
        Return True if this asset has metadata.

        :return: bool
        """
        return not self._get_metadata() is None

    def _get_metadata(self):
        """
        Protected property to read the metadata from the DDO object.

        :return:
        """
        result = None
        metadata_service = self._ddo.get_service(ServiceTypes.METADATA)
        if metadata_service:
            values = metadata_service.get_values()
            if DDO_SERVICE_METADATA_KEY in values:
                result = values[DDO_SERVICE_METADATA_KEY]
        return result

    @property
    def is_valid(self):
        """
        Return True if this asset has a valid DDO and DID.

        :return: bool
        """
        return self._ddo and self._ddo.is_valid
