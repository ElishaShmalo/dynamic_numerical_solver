from my_code.displayers.second_order_display import Displayer, SecondOrderSolver
from math import cos

def prey_prime(solver, x, v, t):
        return v

def predetor_prime(solver, x, v, t):
    return  cos(t) - 2*v + (1/2 * x * (1- (x ** 2)))

def predetor_prime2(solver, x, v, t):
    return  - 2*v + (1/2 * x * (1- (x ** 2)))

displayer = Displayer(
    [
        SecondOrderSolver(0, 0, {"dt": 0.01, "time_range": 2}, {"x": prey_prime, "v": predetor_prime}),
        SecondOrderSolver(0, 0, {"dt": 0.01, "time_range": 2}, {"x": prey_prime, "v": predetor_prime2})
        ]
    )
displayer.loop()
