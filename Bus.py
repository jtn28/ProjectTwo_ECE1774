class Bus:
    # Defining the Counter, used to give each bus its index
    # Starting at 0 since Python matrices and lists start at the 0 index
    counter = 0
    # Constructor for the class
    def __init__(self, name:str, baseKV:float):
        # Attributes
        self.name = name
        self.baseKV = baseKV
        # Defining and incrementing the bus index
        self.index = Bus.counter
        Bus.counter += 1

    def __repr__(self):
        return f"Bus(name={self.name}, baseKV={self.baseKV})"

if __name__ == '__main__':
    # Test creation of object
    Bus1 = Bus("Bus1", 20)
    Bus2 = Bus("Bus2", 230)
    print(Bus1.name, Bus1.baseKV, Bus1.index)
    print(Bus2.name, Bus2.baseKV, Bus2.index)
    print(Bus1.counter, Bus2.counter)

