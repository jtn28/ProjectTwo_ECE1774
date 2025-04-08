class Conductor:
    def __init__(self, name:str, diameter:float, GMR:float, resistance:float, ampacity:float):
        """
        Defines a conductor in terms of the Aluminum Company of America Table A.4 for characteristics of ACSR
        Parameters:
            name(str): name of the conductor
            diameter(float): diameter of the conductor
            GMR(float): GMR of the conductor
            resistance(float): resistance of the conductor
            ampacity(float): ampacity of the conductor
        """
        self.name = name
        self.diameter = diameter
        self.GMR = GMR
        self.resistance = resistance
        self.ampacity = ampacity

if __name__ == "__main__":
    cardinal = Conductor("Cardinal", 1.196/12, 0.0403, 0.1128, 1010)