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
            return 1.091 * (self.conductor.diameter / 2 * self.spacing ** 4) ** (1 / 4)
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

