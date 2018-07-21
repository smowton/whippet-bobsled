
class Model:

    def __init__(self):
        # a set of 3-tuples
        self.filled_coords = set()

    def filled(self, coord):
        return coord in self.filled_coords

