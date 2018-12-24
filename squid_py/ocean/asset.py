"""Ocean module."""

import hashlib
import json
import logging

from squid_py.ddo import DDO
from squid_py.did import did_to_id, id_to_did
from squid_py.ocean.ocean_base import OceanBase
from squid_py.service_agreement.service_types import ServiceTypes

DDO_SERVICE_METADATA_KEY = 'metadata'


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

        :param did: `did:op:0x...`, the 0x id portion must be of length 64 (or 32 bytes)
        :param publisher_id:
        :param ddo: DDO instance
        """

        self._ddo = ddo
        self.publisher_id = publisher_id
        self.asset_id = None
        if self._ddo and self._ddo.is_did_assigend() and self._ddo.is_valid:
            self.assign_did_from_ddo()
        else:
            self.asset_id = hashlib.sha256('assetId'.encode('utf-8')).hexdigest()

        OceanBase.__init__(self, self.asset_id)

    def __str__(self):
        return "Asset {}, publisher: {}".format(self.did, self.publisher_id)

    def assign_did_from_ddo(self):
        """
        #TODO: This is a temporary hack, need to clearly define how DID is assigned!
        :return:
        """
        self.asset_id = did_to_id(self._ddo.did)

    @property
    def did(self):
        """
        Return the DID for this asset.

        :return: DID
        """
        if not self._ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self._ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

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
        logging.debug("Asset {} created from ddo file {} ".format(asset.did, json_file_path))
        return asset

    @classmethod
    def from_ddo_dict(cls, dictionary):
        """
        Return a new Asset object from DDO dictionary.

        :param dictionary: dict
        :return: Asset
        """
        asset = cls(ddo=DDO(dictionary=dictionary))
        logging.debug("Asset {} created from ddo dict {} ".format(asset.asset_id, dictionary))
        return asset

    @classmethod
    def create_from_metadata_file(cls, filename, service_endpoint):
        """
        Return a new Asset object from a metadata JSON file.

        :param filename:
        :param service_endpoint:
        :return:
        """
        if filename:
            with open(filename, 'r') as file_handle:
                metadata = json.load(file_handle)
                return Asset.create_from_metadata(metadata, service_endpoint)
        return None

    @classmethod
    def create_from_metadata(cls, metadata, service_endpoint):
        """
        Return a new Asset object from a metadata dictionary.

        :param metadata:
        :param service_endpoint:
        :return:
        """
        # calc the asset id
        asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()

        # generate a DID from an asset_id
        new_did = id_to_did(asset_id)

        # create a new DDO
        new_ddo = DDO(new_did)
        # add a signature
        private_password = new_ddo.add_signature()
        # add the service endpoint with the meta data
        new_ddo.add_service(ServiceTypes.METADATA, service_endpoint,
                            values={DDO_SERVICE_METADATA_KEY: metadata})
        # add the static proof
        new_ddo.add_proof(0, private_password)
        # create the asset object
        this_asset = cls(ddo=new_ddo)
        logging.debug("Asset {} created from metadata {} ".format(this_asset.asset_id, metadata))
        return this_asset

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

    def get_id(self):
        """
        Return asset did.

        :return: DID
        """
        return self.asset_id

    def generate_did(self):
        """
        During development, the DID can be generated here for convenience.

        :return: DID
        """
        if not self.ddo:
            raise AttributeError("No DDO object in {}".format(self))
        if not self.ddo.is_valid:
            raise ValueError("Invalid DDO object in {}".format(self))

        metadata = self._get_metadata()
        if not metadata:
            raise ValueError("No metadata in {}".format(self))

        if not 'base' in metadata:
            raise ValueError("Invalid metadata in {}".format(self))

        self.asset_id = hashlib.sha256(json.dumps(metadata['base']).encode('utf-8')).hexdigest()
        self._ddo = self._ddo.create_new('did:op:%s' % self.asset_id)
