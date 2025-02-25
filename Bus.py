class Bus:
    # Defining the Counter, used to give each bus its index
    # Starting at 0 since Python matrices and lists start at the 0 index
    counter = 0
    # Constructor for the class
    def __init__(self, name:str, baseKV:float, vpu:float = 1, delta:float = 0, bus_type:str = 'Slack'):
        # Attributes
        self.name = name
        self.baseKV = baseKV
        # Milestone 5 attributes
        self.vpu = vpu
        self.delta = delta
        if bus_type == 'Slack' or bus_type == 'PQ' or bus_type == 'PV':
            self.type = bus_type
        else:
            print(f"Invalid bus type in Bus {Bus.counter}, bus_type input variable was {bus_type}, setting bus_type to null")
            self.type = 'null'
        # Defining and incrementing the bus index
        self.index = Bus.counter
        Bus.counter += 1

    def __repr__(self):
        return f"Bus(name={self.name}, baseKV={self.baseKV}, vpu={self.vpu}, delta={self.delta}, type={self.type}, index={self.index})"

if __name__ == '__main__':
    # Test creation of object
    Bus1 = Bus("Bus1", 20)
    Bus2 = Bus("Bus2", 230, 1, 60, 'PV')
    Bus3 = Bus("Bus3", 400, 1, -60, 'PQ')
    Bus4 = Bus("Bus4", 50, 1, 120, 'PL')

    print(repr(Bus1))
    print(repr(Bus2))
    print(repr(Bus3))
    print(repr(Bus4))

