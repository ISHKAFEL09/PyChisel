class Singleton(type):
    def __init__(cls, *args, **kwargs):
        if getattr(cls, 'apply', None) is None:
            raise TypeError(f'singleton class {cls.__name__} should implement apply()!')
        super().__init__(*args, **kwargs)

