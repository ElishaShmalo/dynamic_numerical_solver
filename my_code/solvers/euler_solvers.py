import matplotlib.pyplot as plt
from math import sqrt

def x_prime(solver, x, v, t):
    return v

def v_prime(solver, x, v, t):
    return  -solver.parameters["k"]/solver.parameters["m"]*x - solver.parameters["b"]/solver.parameters["m"]*v

def euler_menthod(solver, point, index_to_solve, t, dt, deriv_func):
    return point[index_to_solve] + deriv_func(solver, point[0], point[1], t) * dt

class SecondOrderSolver:

    def __init__(self, x0=0, y0=0, parameters={"dt": 1, "time_range": 100, "k": 2, "b": 0, "m": 1}, derivatives = {"x": x_prime, "v": v_prime}) -> None:
        self.parameters = parameters
        self.derivatives = derivatives

        self.p0 = [x0, y0]
        self.points = [self.p0]
        self.arrow_pt = [self.p0[0], self.p0[1]]

    def calculate_points(self, _dt=None, t_range=None):
        self.points = [[self.p0[0], self.p0[1]]]
        dt = 0
        if _dt:
            dt = _dt
        else:
            dt = self.parameters["dt"]

        time_range = 0
        if t_range:
            time_range = t_range
        else:
            time_range = self.parameters["time_range"]

        try: 
            t = 0
            while t < time_range/2:
                current_point = self.points[-1]

                current_x = current_point[0]
                current_v = current_point[1]

                next_x = current_x + (self.derivatives["x"](self, current_x, current_v, t) * dt)
                next_v = current_v + (self.derivatives["v"](self, current_x, current_v, t) * dt)
                
                self.points.append([next_x, next_v])

                t += dt
            
            t = 0
            while t > -time_range/2:
                current_point = self.points[0]

                current_x = current_point[0]
                current_v = current_point[1]

                next_x = current_x + (self.derivatives["x"](self, current_x, current_v, t) * -dt)
                next_v = current_v + (self.derivatives["v"](self, current_x, current_v, t) * -dt)

                self.points.insert(0, [next_x, next_v])
                

                t -= dt
        except Exception as e:
            print("Hey, there was an error:")
            print(e)
            self.points = [[self.p0[0], self.p0[1]]]


        return self.points
    
    def plot(self, x0, v0, t_range, dt):
        self.parameters["time_range"] = t_range
        self.parameters["dt"] = dt
        self.p0 = [x0, v0]
        self.points = [self.p0]

        self.calculate_points()

        x_values = [point[0] for point in self.points]
        y_values = [point[1] for point in self.points]
        
        plt.plot(x_values, y_values, marker='o', linestyle='-', markersize=1)
        plt.title(f'Simple Curve: (x0, v0) = ({x0, v0}) | dt = {dt}')
        plt.xlabel('X')
        plt.ylabel('V')
        plt.grid(True)
        plt.show()
    
    def copy(self):

        params = {key:self.parameters[key] for key in self.parameters}
        ders = {key:self.derivatives[key] for key in self.derivatives}

        return SecondOrderSolver(parameters=params, derivatives=ders)


if __name__ == "__main__":
    test_param = {
        "dt": 0.01,
        "time_range": 10,
        "k": 2,
        "b": 0
    }

    second_order_solver = SecondOrderSolver(1, 0, 0.01)



    second_order_solver.plot(1, 1, 100, 0.0001)
