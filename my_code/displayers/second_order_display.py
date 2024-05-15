import pygame as pg
from ..solvers.euler_solvers import SecondOrderSolver
from typing import List
from ..utils.buttons import *
from ..utils.rendering import *
import random as rn
import sys

class Displayer:

    SCREEN_WIDTH = 1150
    SCREEN_HEIGHT = 700

    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 700

    PARAM_SLIDER_X = 140
    PARAM_SLIDER_Y = 200

    def __init__(self, solvers: List[SecondOrderSolver]):
        pg.init()
        self.win = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pg.display.set_caption("Solver Display")
        self.clock = pg.time.Clock()

        self.offset0 = [-self.DISPLAY_WIDTH//2, -self.DISPLAY_HEIGHT//2]
        self.window_offset = [0, 0]
        self.offset = [self.window_offset[0] + self.offset0[0], self.window_offset[1] + self.offset0[1]]

        self.running = True

        self.pre_drag_mouse_posG = pg.mouse.get_pos()

        self.dragging = False
        self.resetting_initial_cond = [False, 0]

        self.drawing_grid_size = [self.DISPLAY_WIDTH // 10, self.DISPLAY_HEIGHT // 10]

        self.scale = 100

        self.location_txt = pg.font.SysFont(None, 20)

        self.scalling_factor = 1

        self.solvers = solvers
        self.curve_colors = [rn.choice(CURVE_COLORS) for _ in range(len(solvers))]
        for solver in self.solvers:
            solver.calculate_points()

        self.menu_bar = pg.Surface((self.SCREEN_WIDTH - self.DISPLAY_WIDTH, self.SCREEN_HEIGHT))

        self.sliders = {}
        for i, solver in enumerate(self.solvers):
            self.sliders[solver] = {}
            for j, param in enumerate(solver.parameters):
                value = solver.parameters[param]
                s = Slider(pg.Rect(self.PARAM_SLIDER_X, self.PARAM_SLIDER_Y + j * 20, 200, 20), min_value=value-100, max_value=value+100, current_value=value, text=param)
                s.active = i ==  self.resetting_initial_cond[1]
                s.showing = i ==  self.resetting_initial_cond[1]
                if param == "dt":
                    s.min_value = 0.00001
                    s.max_value = 0.1
                if param == "time_range":
                    s.min_value = 1
                s.calculate_slider_circle_pos()
                self.sliders[solver][param] = s


        self.buttons = {
            "display_pts": BooleanButton(pg.FRect(140, 10, 20, 20), text="Render Points", text_color=(0, 0, 0), color=(0, 128, 128)),
            "return_home": SinglePressButton(pg.FRect(10, 10, 50, 20), border=True, text="Home", text_color=(0, 0, 0), on_press_function=self.return_home),
            "add_initial_cond": SinglePressButton(pg.FRect(30, 60, 150, 20), border=True, text="Add Initial Condition", text_color=(0, 0, 0), on_press_function=self.new_initial_cond),
            "delete_initial_cond": SinglePressButton(pg.FRect(30, 80, 150, 20), border=True, text="Delete Initial Condition", text_color=(0, 0, 0), on_press_function=self.del_initial_cond),
        }

        for solver in self.solvers:
            for param in solver.parameters:  
                self.buttons[f"{solver}|{param}"] = self.sliders[solver][param]

    def del_initial_cond(self):
        if self.resetting_initial_cond[1] < len(self.solvers):
            solver_to_remove = self.solvers[self.resetting_initial_cond[1]]
            self.sliders.pop(solver_to_remove)
            self.solvers.remove(solver_to_remove)

            button_keys = []
            for key in self.buttons:
                if f"{solver_to_remove}" in key:
                    button_keys.append(key)
            for key in button_keys:
                self.buttons.pop(key)

            self.resetting_initial_cond[1] = 0
            for slider in self.sliders[self.solvers[0]].values():
                slider.showing = True
                slider.active = True

    def new_initial_cond(self):
        if self.resetting_initial_cond[1] < len(self.solvers):
            current_slover = self.solvers[self.resetting_initial_cond[1]]
            new_solver = current_slover.copy()

            self.sliders[new_solver] = {}

            for j, param in enumerate(new_solver.parameters):
                value = new_solver.parameters[param]
                s = Slider(pg.Rect(self.PARAM_SLIDER_X, self.PARAM_SLIDER_Y + j * 20, 200, 20), min_value=value-100, max_value=value+100, current_value=value, text=param)
                s.active = False
                s.showing = False
                if param == "dt":
                    s.min_value = 0
                    s.max_value = 0.5
                if param == "time_range":
                    s.min_value = 1
                self.sliders[new_solver][param] = s

            for param in new_solver.parameters:  
                self.buttons[f"{new_solver}|{param}"] = self.sliders[new_solver][param]

            self.curve_colors.append(rn.choice(CURVE_COLORS))
            self.solvers.append(new_solver)

    def return_home(self):
        self.scale = 100
        self.window_offset = [0, 0]
        self.offset = [self.window_offset[0] + self.offset0[0], self.window_offset[1] + self.offset0[1]]

    def loop(self):
        while self.running:
            self.clock.tick(60)
            mouse_pos = pg.mouse.get_pos()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                    return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_rect = pg.FRect(mouse_pos[0], mouse_pos[1], 2, 2)
                    # If we are on the graph
                    if 0 <= mouse_pos[0] < self.DISPLAY_WIDTH:
                        # check if we are clicking on an initial condition
                        for i, solver in enumerate(self.solvers):
                            if self.clicked_initial_cond(mouse_rect, solver.p0):
                                for slider in self.sliders[self.solvers[self.resetting_initial_cond[1]]].values():
                                    slider.showing = False
                                    slider.active = False

                                self.resetting_initial_cond = [True, i]
                                for slider in self.sliders[solver].values():
                                    slider.showing = True
                                    slider.active = True
                                break
                        if not self.resetting_initial_cond[0]:
                            self.dragging = True
                            self.pre_drag_mouse_posG = [mouse_pos[0] + self.offset[0], mouse_pos[1] + self.offset[1]]
                    else: # We are in the menu
                        menu_mouse_pos = [mouse_pos[0]- self.DISPLAY_WIDTH, mouse_pos[1]]
                        buttons = list(self.buttons.values())
                        for i in range(len(buttons)):
                            but = buttons[i]
                            but.pressed(menu_mouse_pos)
                    
                elif event.type == pg.MOUSEBUTTONUP:
                    if self.resetting_initial_cond[0]:
                        self.solvers[self.resetting_initial_cond[1]].calculate_points()
                        self.resetting_initial_cond[0] = False

                    self.dragging = False
                    for button in self.buttons.values():
                        button.is_pressed = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.scalling_factor = 1.1
                    elif event.key == pg.K_DOWN:
                        self.scalling_factor = 0.9
                    elif event.key == pg.K_r:
                        self.solvers[self.resetting_initial_cond[1]].parameters["dt"] = 0.01
                        self.sliders[self.solvers[self.resetting_initial_cond[1]]]["dt"].change_val(0.01)
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_UP or event.key == pg.K_DOWN:
                        self.scalling_factor = 1

            self.update(mouse_pos)
            self.draw()
    
    def update(self, mosue_pos):
        if self.dragging:
            self.drag()
        
        if self.resetting_initial_cond[0]:
            self.reset_initial_cond(self.resetting_initial_cond[1])

        if self.scalling_factor != 1:
            self.zoom()

        self.offset = [self.window_offset[0] + self.offset0[0], self.window_offset[1] + self.offset0[1]]

        menu_mouse_posx = mosue_pos[0] - self.DISPLAY_WIDTH
        for solver_key in self.sliders:
            for param in self.sliders[solver_key]:
                slider = self.sliders[solver_key][param]
                if self.sliders[solver_key][param].update(menu_mouse_posx):
                    solver_key.parameters[param] = slider.current_value
                    solver_key.calculate_points()
    
    def reset_initial_cond(self, ind):
        mouse_pos = pg.mouse.get_pos()
        mouse_posG_to_scale = self.global_pos_to_scale(mouse_pos)

        solver = self.solvers[ind]

        solver.p0[0] = mouse_posG_to_scale[0]
        solver.p0[1] = mouse_posG_to_scale[1]

        solver.calculate_points(max(0.01, solver.parameters["dt"]), min(20, solver.parameters["time_range"]))

    def zoom(self):
        pre_zoom_mouse_posG = self.global_pos_to_scale(pg.mouse.get_pos())

        # self.window_offset[0] *= self.scalling_factor
        # self.window_offset[1] *= self.scalling_factor
        self.scale *= self.scalling_factor

        post_zoom_mouse_posG = self.global_pos_to_scale(pg.mouse.get_pos())
        
        diff_x = post_zoom_mouse_posG[0] - pre_zoom_mouse_posG[0]
        diff_y = post_zoom_mouse_posG[1] - pre_zoom_mouse_posG[1]

        self.window_offset[0] -= self.scale * diff_x
        self.window_offset[1] -= -self.scale * diff_y

    def drag(self):
        current_mouse_pos = pg.mouse.get_pos()
        current_mouse_posG = [current_mouse_pos[0] + self.offset[0], current_mouse_pos[1] + self.offset[1]]
        diff_x = (current_mouse_posG[0] - self.pre_drag_mouse_posG[0])
        diff_y = (current_mouse_posG[1] - self.pre_drag_mouse_posG[1])

        self.window_offset[0] -= 0.75 * diff_x
        self.window_offset[1] -= 0.75 * diff_y

    def draw(self):
        self.win.fill((200, 200, 200))

        self.draw_grid_with_values()
        self.draw_curve()

        self.draw_menu()

        pg.display.update()
    
    def draw_menu(self):
        self.menu_bar.fill((150, 150, 150))

        for but in self.buttons.values():
            but.show(self.menu_bar)

        self.win.blit(self.menu_bar, (self.DISPLAY_WIDTH, 0))

    def global_pos_to_scale(self, win_pos):
        # takes pixle cords and returns the global position (scaled)
        x = (win_pos[0] + self.offset[0]) / self.scale
        y = -((win_pos[1] + self.offset[1])/ self.scale)
        if y == 0:
            y = 0
        return [x, y]
    
    def win_pos_from_global_scaled(self, global_pos):
        x = (global_pos[0] * self.scale) - self.offset[0]
        y = (global_pos[1] * -self.scale) - self.offset[1]
        return [x, y]

    def draw_grid_with_values(self):

        for i in range(-1, 11):
            y_loc = -self.offset[1] % self.drawing_grid_size[1] + i * self.drawing_grid_size[1]
            x_loc = -self.offset[0] % self.drawing_grid_size[0] + i * self.drawing_grid_size[0]

            y_loc -= (y_loc // self.DISPLAY_HEIGHT) * self.drawing_grid_size[1]
            x_loc -= (x_loc // self.DISPLAY_WIDTH) * self.drawing_grid_size[0]

            pg.draw.line(self.win, (150, 150, 150), (0, y_loc), (self.DISPLAY_WIDTH, y_loc))
            pg.draw.line(self.win, (150, 150, 150), (x_loc, 0), (x_loc, self.DISPLAY_HEIGHT))

            global_pos_scaled = self.global_pos_to_scale([x_loc, y_loc])

            text = self.location_txt.render("{:.3e}".format(global_pos_scaled[0]), True, (100, 100, 100))
            self.win.blit(text, (x_loc, self.DISPLAY_HEIGHT - 20))

            # Display vertical values
            text = self.location_txt.render("{:.3e}".format(global_pos_scaled[1]), True, (100, 100, 100))
            self.win.blit(text, (5, y_loc))
        
        pg.draw.line(self.win, (0, 0, 0), (0, -self.offset[1]), (self.DISPLAY_WIDTH, -self.offset[1]))
        pg.draw.line(self.win, (0, 0, 0), (-self.offset[0], 0), (-self.offset[0], self.DISPLAY_HEIGHT))

    def draw_curve(self):
        top_left = self.global_pos_to_scale((-10, -10))
        bottom_right = self.global_pos_to_scale((self.DISPLAY_WIDTH+10, self.DISPLAY_HEIGHT+10))

        for c, solver in enumerate(self.solvers):
            color = self.curve_colors[c]
            for i, pt in enumerate(solver.points):
                not_last = i != len(solver.points) - 1
                nxt_pt = pt
                if not_last:
                    nxt_pt = solver.points[i+1]
                draw_anyway = top_left[0] <= nxt_pt[0] <= bottom_right[0] and top_left[1] >= nxt_pt[1] >= bottom_right[1]
                if (top_left[0] <= pt[0] <= bottom_right[0] and top_left[1] >= pt[1] >= bottom_right[1]) or draw_anyway:
                    win_pt = self.win_pos_from_global_scaled(pt)
                    if self.buttons["display_pts"].value:
                        pg.draw.circle(self.win, color, win_pt, 3)
                    if not_last:
                        next_win_pt = self.win_pos_from_global_scaled(nxt_pt)
                        pg.draw.line(self.win, color, win_pt, next_win_pt, 3)

            # drawing the dircetion of the curve (could use some optimization)
            # pg.draw.line(self.win, color, self.win_pos_from_global_scaled(solver.p0), self.win_pos_from_global_scaled([solver.arrow_pt[0], solver.arrow_pt[1]]), 4)
            
            pg.draw.circle(self.win, (0, 50, 32), self.win_pos_from_global_scaled(solver.p0), 10)


        if self.resetting_initial_cond[1] < len(self.solvers):
            pg.draw.circle(self.win, (255, 100, 100), self.win_pos_from_global_scaled(self.solvers[self.resetting_initial_cond[1]].p0), 11, 2)

    def clicked_initial_cond(self, mouse_rect, pt):
        solver_rect = pg.FRect(0, 0, 20, 20)
        solver_rect.center = self.win_pos_from_global_scaled(pt)
        return mouse_rect.colliderect(solver_rect)

    def quit(self):
        self.running = False
        pg.display.update()
        pg.display.quit()
        pg.quit()
        raise SystemExit

