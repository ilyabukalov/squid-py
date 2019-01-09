from squid_py.brizo.brizo import Brizo


class BrizoProvider(object):
    _brizo = None

    @staticmethod
    def get_brizo():
        if BrizoProvider._brizo is None:
            BrizoProvider._brizo = Brizo()

        return BrizoProvider._brizo

    @staticmethod
    def set_brizo(brizo):
        BrizoProvider._brizo = brizo
