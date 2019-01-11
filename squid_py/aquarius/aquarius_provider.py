from squid_py.aquarius.aquarius import Aquarius


class AquariusProvider(object):
    """Provides the Aquarius instance."""
    _aquarius = None

    @staticmethod
    def get_aquarius(url=None):
        """ Get an Aquarius instance."""
        if not AquariusProvider._aquarius:
            AquariusProvider._aquarius = Aquarius(url)

        return AquariusProvider._aquarius

    @staticmethod
    def set_aquarius(aquarius):
        """
         Set an Aquarius instance.

        :param aquarius: Aquarius
        :return:  New Aquarius instance.
        """
        AquariusProvider._aquarius = aquarius
