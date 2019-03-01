"""Ocean module."""
import logging

logger = logging.getLogger(__name__)


class OceanTemplates:
    """Class"""

    def __init__(self, keeper, config):
        self._keeper = keeper
        self._config = config
        self.access_template_id = self._keeper.escrow_access_secretstore_template.address

    def propose(self, template_address, account):
        """

        :param template_address:
        :param account:
        :return:
        """
        try:
            proposed = self._keeper.template_manager.propose_template(template_address, account)
            return proposed
        except ValueError as err:
            template_values = self._keeper.template_manager.get_template(template_address)
            if not template_values:
                logger.warning(f'Propose template failed: {err}')
                return False

            if template_values.state != 1:
                logger.warning(f'Propose template failed, current state is set to {template_values.state}')
                return False

            return True

    def approve(self, template_address, account):
        try:
            approved = self._keeper.template_manager.approve_template(template_address, account)
            return approved
        except ValueError as err:
            template_values = self._keeper.template_manager.get_template(template_address)
            if not template_values:
                logger.warning(f'Approve template failed: {err}')
                return False

            if template_values.state == 1:
                logger.warning(f'Approve template failed, this template is '
                               f'currently in "proposed" state.')
                return False

            if template_values.state == 3:
                logger.warning(f'Approve template failed, this template appears to be '
                               f'revoked.')
                return False

            if template_values.state == 2:
                return True

            return False

    def revoke(self, template_address, account):
        try:
            revoked = self._keeper.template_manager.revoke_template(template_address, account)
            return revoked
        except ValueError as err:
            template_values = self._keeper.template_manager.get_template(template_address)
            if not template_values:
                logger.warning(f'Cannot revoke template since it does not exist: {err}')
                return False

            logger.warning(f'Only template admin or owner can revoke a template: {err}')
            return False
