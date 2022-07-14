

class Singleton(type):

    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
            return cls._instance
        else:
            return cls._instance

class ClipBoard(metaclass=Singleton):

    def __init__(self, data=None, form=None):
        self._data = data
        self._form = form

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._form.statusBar.showMessage(f"Clipboard: {data}")



