from squid_py.aquarius.aquarius import Aquarius


class AquariusProvider(object):
    _aquarius = None

    @staticmethod
    def get_aquarius(url=None):
        if not AquariusProvider._aquarius:
            AquariusProvider._aquarius = Aquarius(url)

        return AquariusProvider._aquarius

    @staticmethod
    def set_aquarius(aquarius):
        AquariusProvider._aquarius = aquarius
