import numpy as np

class Settings:
    frequency = 60
    base_power = 100e6
    def __init__(self, frequency:float = 60, base_power:float = 100e6):
        Settings.frequency = frequency
        Settings.base_power = base_power
