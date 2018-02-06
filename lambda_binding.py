
def create_adder_functions():
    return [lambda x: x + i for i in range(5)]


for adder_function in create_adder_functions():
    print(adder_function(2))
