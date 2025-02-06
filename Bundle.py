from Conductor import Conductor
class Bundle:
    # Bundle class
    # Creating the init, needs to have a reference to the conductor class to function, will push for now
    # and update to change the conductor references if needed.
    def __init__(self, name:str, num_conductors:int, spacing:float, conductor:Conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor

    def calculate_dsc(self):
        # Start by grabbing the GMR from the conductor class, then calculate
        # Assuming the diameter is given in feet, may need to adjust this later
        if self.num_conductors == 1:
            return self.conductor.diameter / 2
        elif self.num_conductors == 2:
            return (self.conductor.diameter / 2 * self.spacing) ** (1 / 2)
        elif self.num_conductors == 3:
            return (self.conductor.diameter / 2 * self.spacing ** 2) ** (1 / 3)
        elif self.num_conductors == 4:
            return 1.091 * (self.conductor.diameter / 2 * self.spacing ** 3) ** (1 / 4)
        else:
            # Will only have the values of bundling for 1 to 4 for now, will add 6 and 8 if needed
            print("Invalid bundle size, choose a value between 1 and 4")
            return 0

    def calculate_dsl(self):
        # Start by grabbing the GMR from the conductor class, then calculate
        if self.num_conductors == 1:
            return self.conductor.GMR
        elif self.num_conductors == 2:
            return (self.conductor.GMR * self.spacing) ** (1 / 2)
        elif self.num_conductors == 3:
            return (self.conductor.GMR * self.spacing**2) ** (1 / 3)
        elif self.num_conductors == 4:
            return 1.091 * (self.conductor.GMR * self.spacing**3) ** (1 / 4)
        else:
            # Will only have the values of bundling for 1 to 4 for now, will add 6 and 8 if needed
            print("Invalid bundle size, choose a value between 1 and 4")
            return 0

if __name__ == "__main__":
    # Just runs a test with all 4 different potential bundles, using a cardinal conductor for this
    cardinal = Conductor("Cardinal", 1.196 / 12, 0.0403, 0.1128, 1010)
    test = Bundle('testBundle', 1, 3, cardinal)
    dsc = test.calculate_dsc()
    dsl = test.calculate_dsl()
    print(f'For {test.num_conductors} Conductors with a spacing of {test.spacing} feet for a {cardinal.name} Conductor:')
    print(f'DSC = {dsc:.2f} and DSL = {dsl:.2f}')
    test.num_conductors = 2
    dsc = test.calculate_dsc()
    dsl = test.calculate_dsl()
    print(f'For {test.num_conductors} Conductors with a spacing of {test.spacing} feet for a {cardinal.name} Conductor:')
    print(f'DSC = {dsc:.2f} and DSL = {dsl:.2f}')
    test.num_conductors = 3
    dsc = test.calculate_dsc()
    dsl = test.calculate_dsl()
    print(f'For {test.num_conductors} Conductors with a spacing of {test.spacing} feet for a {cardinal.name} Conductor:')
    print(f'DSC = {dsc:.2f} and DSL = {dsl:.2f}')
    test.num_conductors = 4
    dsc = test.calculate_dsc()
    dsl = test.calculate_dsl()
    print(f'For {test.num_conductors} Conductors with a spacing of {test.spacing} feet for a {cardinal.name} Conductor:')
    print(f'DSC = {dsc:.2f} and DSL = {dsl:.2f}')