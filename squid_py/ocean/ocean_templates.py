from squid_py.agreements.service_agreement_template import ServiceAgreementTemplate
from squid_py.agreements.service_types import ACCESS_SERVICE_TEMPLATE_ID
from squid_py.agreements.utils import get_sla_template_path, register_service_agreement_template


class OceanTemplates:

    def __init__(self, keeper, config):
        self._keeper = keeper
        self._config = config
        self.access_template_id = ACCESS_SERVICE_TEMPLATE_ID

    def create(self, template_id, account):
        """

        :param template_id: hex str id of the template to create on-chain
        :param account: Account instance to be owner of this template
        :return: bool
        """
        if not template_id:
            template_id = ACCESS_SERVICE_TEMPLATE_ID

        template = ServiceAgreementTemplate.from_json_file(get_sla_template_path())
        assert template_id == ACCESS_SERVICE_TEMPLATE_ID
        assert template_id == template.template_id
        template_owner = self._keeper.service_agreement.get_template_owner(template_id)
        if not template_owner:
            template = register_service_agreement_template(
                self._keeper.service_agreement,
                account,
                template,
                self._keeper.network_name
            )

        return template is not None
