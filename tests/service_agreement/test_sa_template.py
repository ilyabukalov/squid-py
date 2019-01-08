from squid_py import ServiceAgreementTemplate
from squid_py.keeper import Keeper
from squid_py.service_agreement.utils import get_sla_template_dict, get_sla_template_path, register_service_agreement_template
from squid_py.utils.utilities import generate_prefixed_id


def test_setup_service_agreement_template(publisher_ocean_instance):
    ocn = publisher_ocean_instance
    sa = Keeper.get_instance().service_agreement
    template_dict = get_sla_template_dict(get_sla_template_path())
    template_dict['id'] = generate_prefixed_id()
    sla_template = ServiceAgreementTemplate(template_json=template_dict)
    sla_template = register_service_agreement_template(
        sa, publisher_ocean_instance.main_account, sla_template
    )

    # verify new sa template is registered
    assert sa.get_template_owner(sla_template.template_id) == ocn.main_account.address
