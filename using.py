from my_code.displayers.second_order_display import Displayer, SecondOrderSolver



def prey_prime(solver, x, v):
        return solver.parameters["a"]*x - solver.parameters["b"]*v*x

def predetor_prime(solver, x, v):
    return  -solver.parameters["c"]*v + solver.parameters["d"]*v*x

displayer = Displayer(
    [
        SecondOrderSolver(1, 0, parameters={"dt": 0.01, "time_range": 100, "k": 5, "b": 2, "m": 1}),
        SecondOrderSolver(1, 1, {"dt": 0.01, "time_range": 100, "a":1, "b": 2, "c": 3, "d": 4}, {"x": prey_prime, "v": predetor_prime})
        ]
    )
displayer.loop()


