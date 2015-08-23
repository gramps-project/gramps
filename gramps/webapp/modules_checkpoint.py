import sys

class ModulesCheckpoint(object):
    def __init__(self):
        self.original = sys.modules.copy()

    def reset(self):
        # clear modules:
        for key in list(sys.modules.keys()):
            del(sys.modules[key])
        # load previous:
        for key in self.original:
            sys.modules[key] = self.original[key]
