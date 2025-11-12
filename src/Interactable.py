from .Obstacles import _Obstacle


class _Interactable:
    def __init__(self, *args):
        self.args = args
        self.interacted_once = False

    def interact():
        ...