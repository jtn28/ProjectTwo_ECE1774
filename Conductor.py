class Conductor:
    def __init__(self, name:str, diameter:float, GMR:float, resistance:float, ampacity:float):
        self.name = name
        self.diameter = diameter
        self.GMR = GMR
        self.resistance = resistance
        self.ampacity = ampacity

if __name__ == "__main__":
    cardinal = Conductor("Cardinal", 1.196/12, 0.0403, 0.1128, 1010)