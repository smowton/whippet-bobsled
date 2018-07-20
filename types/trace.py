
class Trace:
    
    class Halt:
        def __init__(self):
            pass

    class Wait:
        def __init__(self):
            pass

    class Flip:
        def __init__(self):
            pass

    class SMove:
        def __init__(self, distance):
            self.distance = distance

    class LMove:
        def __init__(self, distance1, distance2):
            self.distance1 = distance1
            self.distance2 = distance2

    class FusionP:
        def __init__(self, distance):
            self.distance = distance

    class FusionS:
        def __init__(self, distance):
            self.distance = distance

    class Fission:
        def __init__(self, distance, seeds_kept):
            self.distance = distance
            self.seeds_kept = seeds_kept

    class Fill:
        def __init__(self, distance):
            self.distance = distance

