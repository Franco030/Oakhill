import math
import random

class MathLib:
    """
    Standard math library for FER
    """

    @staticmethod
    def random_int(min_val, max_val):
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float():
        return random.random()

    @staticmethod
    def cos(val):
        return math.cos(val)
    
    @staticmethod
    def sin(val):
        return math.sin(val)
    
    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)