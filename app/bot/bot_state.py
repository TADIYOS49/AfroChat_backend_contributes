from app.utils.singeleton import SingletonMeta
from collections import defaultdict


class GlobalState(defaultdict, metaclass=SingletonMeta):
    def __init__(self):
        # Set the default factory to dict, which creates a new dictionary as the default value
        super().__init__(dict)

    pass


State = GlobalState()
