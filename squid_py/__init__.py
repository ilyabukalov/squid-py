__author__ = """OceanProtocol"""
__version__ = '0.3.2'

from .config import (
    Config
)
from .config_provider import (
    ConfigProvider,
)
from .exceptions import (OceanDIDAlreadyExist, OceanDIDNotFound,
                         OceanDIDUnknownValueType, OceanInvalidContractAddress,
                         OceanInvalidMetadata, OceanInvalidServiceAgreementSignature,
                         OceanKeeperContractsNotFound, OceanServiceAgreementExists)
from .ocean import (
    Ocean,
)
