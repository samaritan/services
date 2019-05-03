from zope import interface


class IRepository(interface.Interface):
    def get_changes():
        pass

    def get_commits():
        pass

    def get_developers():
        pass

    def get_files():
        pass

    def get_modules():
        pass

    def get_patches():
        pass

    def get_path():
        pass

    def get_version():
        pass
