import logging

from squid_py.service_agreement import ACCESS_SERVICE_TEMPLATE_ID
from squid_py.keeper import Keeper


class Diagnostics:
    @staticmethod
    def check_deployed_agreement_templates():
        keeper = Keeper.get_instance()
        # Check for known service agreement templates
        template_owner = keeper.service_agreement.get_template_owner(ACCESS_SERVICE_TEMPLATE_ID)
        if not template_owner or template_owner == 0:
            logging.info('The `Access` Service agreement template "%s" is not deployed to '
                         'the current keeper network.', ACCESS_SERVICE_TEMPLATE_ID)
        else:
            logging.info('Found service agreement template "%s" of type `Access` deployed in '
                         'the current keeper network published by "%s".',
                         ACCESS_SERVICE_TEMPLATE_ID, template_owner)
