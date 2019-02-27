"""Ocean module."""
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID


class OceanTemplates:
    """Class"""

    def __init__(self, keeper, config):
        self._keeper = keeper
        self._config = config
        self.access_template_id = ACCESS_SERVICE_TEMPLATE_ID

    def propose(self, template_address, account):
        return

    def approve(self, template_address, account):
        return

    def revoke(self, template_address, account):
        return
