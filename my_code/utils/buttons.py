import pygame as pg

class Button:
    def __init__(self, rect=pg.Rect(0, 0, 10, 10), color=(0, 0, 0), border=False, border_color=(0, 0, 0), text=None, text_color=(50, 50, 50), font=None, font_size=20) -> None:
        self.rect = rect
        self.pos = list(rect.center)
        self.size = [rect.width, rect.height]
        self.color = color
        self.border = border
        self.border_color = border_color
        self.text = text
        self.text_color = text_color
        self.is_pressed = False

        self.active = True
        self.showing = True

        if font:
            self.font = pg.font.Font(font, font_size)
        else:
            self.font = pg.font.Font(None, font_size)
        
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def pressed(self, mouse_pos):
        if not self.active:
            return
        mouse_rect = pg.FRect(mouse_pos[0], mouse_pos[1], 1, 1)
        if self.rect.colliderect(mouse_rect):
            self.pressed_action()
    
    def pressed_action(self):
        pass

    def update(self):
        pass

    def show(self, surf: pg.Surface):
        if not self.showing:
            return
        self.render_button(surf)
        if self.text:
            self.render_text(surf)
    
    def render_button(self, surf: pg.Surface):
        pg.draw.circle(surf, self.color, self.rect.center, 10)

    def render_text(self, surf: pg.Surface):
        surf.blit(self.text_surf, self.text_rect)

class BooleanButton(Button):
    def __init__(self, rect=pg.Rect(0, 0, 10, 10), color=(50, 50, 100), off_color = (50, 50, 50), border=True, border_color=(0, 0, 0), default_value=False, text=None, text_color=(50, 50, 50), font=None, font_size=20) -> None:
        super().__init__(rect, color, border, border_color, text, text_color, font, font_size)
        self.colors = [off_color, color]

        self.value = default_value

        self.current_color = self.colors[self.value]

        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5))  # Position text below the button

    def pressed_action(self):
        self.value = not self.value
        self.current_color = self.colors[self.value]
    
    def render_button(self, surf: pg.Surface):
        pg.draw.circle(surf, self.current_color, self.rect.center, self.size[0]//2)
        pg.draw.circle(surf, self.border_color, self.rect.center, self.size[0]//2, 2)

    def render_text(self, surf):
        surf.blit(self.text_surf, self.text_rect)

class SinglePressButton(Button):
    def __init__(self, rect=pg.Rect(0, 0, 10, 10), color=(150, 150, 150), border=False, border_color=(0, 0, 0), on_press_function=None, text=None, text_color=(50, 50, 50), font=None, font_size=20) -> None:
        super().__init__(rect, color, border, border_color, text, text_color, font, font_size)
        self.on_press_function = on_press_function

        self.colors = [self.color, (136, 216, 176)]

        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)  # Position text inside the button

    def pressed_action(self):
        self.is_pressed = True
        if self.on_press_function:
            self.on_press_function()
    
    def render_button(self, surf: pg.Surface):
        pg.draw.rect(surf, self.colors[self.is_pressed], self.rect)
        if self.border:
            pg.draw.rect(surf, self.border_color, self.rect, 2)
    
    def render_text(self, surf):
        surf.blit(self.text_surf, self.text_rect)

class Slider(Button):
    def __init__(self, slider_rect=pg.Rect(0, 0, 200, 20), color=(100, 100, 100), border=True, border_color=(0, 0, 0), min_value=0, max_value=100, current_value=50, text=None, text_color=(50, 50, 50), font=None, font_size=20) -> None:
        self.circle_rect = pg.Rect(0, 0, 10, 10)
        self.circle_rect.center = slider_rect.center
        
        super().__init__(self.circle_rect, color, border, border_color, text, text_color, font, font_size)
        
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.slider_rect = slider_rect
        self.circle_radius = 5
        self.circle_rect.center = self.calculate_slider_circle_pos()

        self.create_txt()

    def calculate_slider_circle_pos(self):
        # Calculate the position of the slider circle based on the current value
        value_range = self.max_value - self.min_value
        relative_position = (self.current_value - self.min_value) / value_range
        slider_width = self.slider_rect.width
        self.circle_rect.center = (self.slider_rect.left + slider_width * relative_position, self.slider_rect.centery)
        return [self.circle_rect.center[0], self.circle_rect.center[1]]

    def pressed_action(self):
        self.is_pressed = True

    def update(self, mouse_x):
        if self.is_pressed:
            # Update the current value based on the slider circle position
            mouse_x = max(self.slider_rect.left + self.circle_radius, min(mouse_x, self.slider_rect.right - self.circle_radius))
            value_range = self.max_value - self.min_value
            slider_width = self.slider_rect.width - self.circle_radius * 2
            relative_position = (mouse_x - self.slider_rect.left - self.circle_radius) / slider_width
            self.current_value = relative_position * value_range + self.min_value
            self.circle_rect.center = (mouse_x, self.circle_rect.center[1])
            
            self.create_txt()
            return True
        return False
    
    def change_val(self, val):
        self.current_value = val
        self.calculate_slider_circle_pos()
        self.circle_rect.centerx = max(self.slider_rect.left + self.circle_radius, min(self.circle_rect.centerx, self.slider_rect.right - self.circle_radius))
        self.create_txt()

    def create_txt(self):
        self.text_surf = self.font.render(f"{self.text}: {round(self.current_value, 4)}", True, self.text_color)
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.right = self.slider_rect.left - 5
        self.text_rect.centery = self.rect.centery

    def render_button(self, surf: pg.Surface):
        pg.draw.rect(surf, self.color, self.slider_rect)
        pg.draw.circle(surf, (200, 200, 200), self.circle_rect.center, self.circle_radius)
        if self.border:
            pg.draw.circle(surf, self.border_color, self.circle_rect.center, self.circle_radius, 1)

    def render_text(self, surf):
        surf.blit(self.text_surf, self.text_rect)