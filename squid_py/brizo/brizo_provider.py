from squid_py.brizo.brizo import Brizo


class BrizoProvider(object):
    """Provides the Brizo instance."""
    _brizo = None

    @staticmethod
    def get_brizo():
        """ Get a Brizo instance."""
        if BrizoProvider._brizo is None:
            BrizoProvider._brizo = Brizo()

        return BrizoProvider._brizo

    @staticmethod
    def set_brizo(brizo):
        """
         Set a Brizo instance.

        :param brizo: Brizo
        :return:  New Brizo instance.
        """
        BrizoProvider._brizo = brizo
