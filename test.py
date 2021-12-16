
class NonDataDescriptor:

    def __set_name__(self, owner, name):
        print('call to __set_name__')
        self.private_name = '_' + name 

    def __get__(self, obj, obj_type=None):
        print('call to __get__')
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        print('call to __set__')
        setattr(obj, self.private_name, value)


class Test:

    data = NonDataDescriptor()

    def __init__(self, data):
        self.data = data 