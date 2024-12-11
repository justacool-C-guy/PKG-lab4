import pygame
import math
import time
from typing import List, Tuple
import numpy as np

pygame.init()

WIDTH = 1200
HEIGHT = 800
CELL_SIZE = 20
GRID_COLOR = (200, 200, 200)
AXIS_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)
POINT_COLOR = (0, 0, 0)
LINE_COLOR = (0, 0, 0)
BACKGROUND = (255, 255, 255)


class RasterizationApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Растровые алгоритмы")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.offset_x = WIDTH // 2
        self.offset_y = HEIGHT // 2
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        self.current_algorithm = "step"
        self.show_smoothed = False
        self.execution_time = 0
        self.buttons = [
            {'text': 'Step', 'rect': pygame.Rect(10, 10, 100, 30), 'algorithm': 'step'},
            {'text': 'DDA', 'rect': pygame.Rect(120, 10, 100, 30), 'algorithm': 'dda'},
            {'text': 'Bresenham', 'rect': pygame.Rect(230, 10, 100, 30), 'algorithm': 'bresenham'},
            {'text': 'Circle', 'rect': pygame.Rect(340, 10, 100, 30), 'algorithm': 'circle'},
            {'text': 'Castle-Pitway', 'rect': pygame.Rect(450, 10, 100, 30), 'algorithm': 'castle'},
            {'text': "Wu's Line", 'rect': pygame.Rect(560, 10, 100, 30), 'algorithm': 'smooth'},
            {'text': 'Clear', 'rect': pygame.Rect(670, 10, 100, 30), 'algorithm': 'clear'}
        ]
        self.drawn_lines = []
        self.drawn_points = []

    def clear(self):
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        self.execution_time = 0
        self.drawn_lines = []
        self.drawn_points = []

    def screen_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        return ((x - self.offset_x) // CELL_SIZE,
                (self.offset_y - y) // CELL_SIZE)

    def grid_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        return (x * CELL_SIZE + self.offset_x,
                self.offset_y - y * CELL_SIZE)

    def draw_grid(self):
        self.screen.fill(BACKGROUND)

        for x in range(0, WIDTH, CELL_SIZE):
            alpha = 255 if x == self.offset_x else 100
            color = (*GRID_COLOR[:3], alpha)
            pygame.draw.line(self.screen, color, (x, 0), (x, HEIGHT))

            grid_x = (x - self.offset_x) // CELL_SIZE
            if grid_x % 5 == 0:
                text = self.font.render(str(grid_x), True, TEXT_COLOR)
                self.screen.blit(text, (x + 5, self.offset_y + 5))

        for y in range(0, HEIGHT, CELL_SIZE):
            alpha = 255 if y == self.offset_y else 100
            color = (*GRID_COLOR[:3], alpha)
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

            grid_y = (self.offset_y - y) // CELL_SIZE
            if grid_y % 5 == 0:
                text = self.font.render(str(grid_y), True, TEXT_COLOR)
                self.screen.blit(text, (self.offset_x + 5, y - 15))

        pygame.draw.line(self.screen, AXIS_COLOR, (self.offset_x, 0),
                         (self.offset_x, HEIGHT), 2)
        pygame.draw.line(self.screen, AXIS_COLOR, (0, self.offset_y),
                         (WIDTH, self.offset_y), 2)

    def draw_buttons(self):
        for button in self.buttons:
            color = (150, 150, 150) if (self.current_algorithm == button['algorithm'] or
                                        (button['algorithm'] == 'smooth' and self.show_smoothed)) else (200, 200, 200)
            pygame.draw.rect(self.screen, color, button['rect'])
            text = self.font.render(button['text'], True, (0, 0, 0))
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

    def draw_coordinates(self):
        if self.start_point:
            start_text = f"Start: ({self.start_point[0]}, {self.start_point[1]})"
            text_surface = self.font.render(start_text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (10, HEIGHT - 60))

        if self.end_point:
            end_text = f"End: ({self.end_point[0]}, {self.end_point[1]})"
            text_surface = self.font.render(end_text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (10, HEIGHT - 30))

    def draw_pixel(self, pos: Tuple[int, int, float]):
        x, y, alpha = pos
        screen_x, screen_y = self.grid_to_screen(x, y)
        color = (*LINE_COLOR, int(255 * alpha))
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, CELL_SIZE, CELL_SIZE))
        self.screen.blit(surface, (screen_x, screen_y - CELL_SIZE))

    def step_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x0, y0, 1.0)]

        x_increment = dx / steps
        y_increment = dy / steps

        x, y = x0, y0
        for _ in range(steps + 1):
            points.append((round(x), round(y), 1.0))
            x += x_increment
            y += y_increment

        return points

    def dda_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x0, y0, 1.0)]

        x_increment = dx / steps
        y_increment = dy / steps

        x, y = x0, y0
        for _ in range(steps + 1):
            points.append((round(x), round(y), 1.0))
            x += x_increment
            y += y_increment

        return points

    def bresenham_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        x, y = x0, y0

        step_x = 1 if x1 > x0 else -1
        step_y = 1 if y1 > y0 else -1

        if dx > dy:
            err = dx / 2
            while x != x1:
                points.append((x, y, 1.0))
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                x += step_x
        else:
            err = dy / 2
            while y != y1:
                points.append((x, y, 1.0))
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                y += step_y

        points.append((x, y, 1.0))
        return points


    def bresenham_circle(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        radius = int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        x = radius
        y = 0
        err = 0

        while x >= y:
            points.extend([
                (x0 + x, y0 + y, 1.0), (x0 + y, y0 + x, 1.0),
                (x0 - y, y0 + x, 1.0), (x0 - x, y0 + y, 1.0),
                (x0 - x, y0 - y, 1.0), (x0 - y, y0 - x, 1.0),
                (x0 + y, y0 - x, 1.0), (x0 + x, y0 - y, 1.0)
            ])
            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

        return points

    def castle_pitway_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        derror = abs(dy / dx) if dx != 0 else 0
        error = 0
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                points.append((y, x, 1.0))
            else:
                points.append((x, y, 1.0))

            error += derror
            if error >= 0.5:
                y += 1 if y1 > y0 else -1
                error -= 1

        return points

    def wu_line_algorithm(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int, float]]:
        def plot(x: int, y: int, brightness: float) -> Tuple[int, int, float]:
            return x, y, brightness

        def ipart(x: float) -> int:
            return math.floor(x)

        def round_nearest(x: float) -> int:
            return ipart(x + 0.5)

        def fpart(x: float) -> float:
            return x - math.floor(x)

        def rfpart(x: float) -> float:
            return 1 - fpart(x)

        points = []

        if abs(y1 - y0) > abs(x1 - x0):
            steep = True
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        else:
            steep = False

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1

        xend = round_nearest(x0)
        yend = y0 + gradient * (xend - x0)
        xgap = rfpart(x0 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)

        if steep:
            points.append(plot(ypxl1, xpxl1, rfpart(yend) * xgap))
            points.append(plot(ypxl1 + 1, xpxl1, fpart(yend) * xgap))
        else:
            points.append(plot(xpxl1, ypxl1, rfpart(yend) * xgap))
            points.append(plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap))

        intery = yend + gradient

        for x in range(xpxl1 + 1, round_nearest(x1)):
            if steep:
                points.append(plot(ipart(intery), x, rfpart(intery)))
                points.append(plot(ipart(intery) + 1, x, fpart(intery)))
            else:
                points.append(plot(x, ipart(intery), rfpart(intery)))
                points.append(plot(x, ipart(intery) + 1, fpart(intery)))
            intery += gradient

        xend = round_nearest(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = fpart(x1 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)

        if steep:
            points.append(plot(ypxl2, xpxl2, rfpart(yend) * xgap))
            points.append(plot(ypxl2 + 1, xpxl2, fpart(yend) * xgap))
        else:
            points.append(plot(xpxl2, ypxl2, rfpart(yend) * xgap))
            points.append(plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap))

        return points

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for button in self.buttons:
                        if button['rect'].collidepoint(x, y):
                            if button['algorithm'] == 'clear':
                                self.clear()
                            else:
                                self.current_algorithm = button['algorithm']
                                self.start_point = None
                                self.end_point = None
                                self.is_drawing = False
                            break
                    else:
                        self.start_point = None
                        self.end_point = None
                        self.start_point = self.screen_to_grid(x, y)
                        self.is_drawing = True

                elif event.type == pygame.MOUSEBUTTONUP and self.is_drawing:
                    x, y = event.pos
                    self.end_point = self.screen_to_grid(x, y)
                    self.is_drawing = False

                    if self.start_point and self.end_point:
                        self.drawn_lines.append({
                            'start': self.start_point,
                            'end': self.end_point,
                            'algorithm': self.current_algorithm
                        })

            self.draw_grid()
            self.draw_buttons()
            self.draw_coordinates()

            for line in self.drawn_lines:
                if line['algorithm'] == 'step':
                    points = self.step_algorithm(*line['start'], *line['end'])
                elif line['algorithm'] == 'dda':
                    points = self.dda_algorithm(*line['start'], *line['end'])
                elif line['algorithm'] == 'bresenham':
                    points = self.bresenham_algorithm(*line['start'], *line['end'])
                elif line['algorithm'] == 'circle':
                    points = self.bresenham_circle(*line['start'], *line['end'])
                elif line['algorithm'] == 'castle':
                    points = self.castle_pitway_algorithm(*line['start'], *line['end'])
                elif line['algorithm'] == 'smooth':
                    points = self.wu_line_algorithm(*line['start'], *line['end'])

                for point in points:
                    self.draw_pixel(point)

            if self.start_point and self.is_drawing:
                current_end = self.screen_to_grid(*pygame.mouse.get_pos())

                start_time = time.perf_counter()

                if self.current_algorithm == 'step':
                    points = self.step_algorithm(*self.start_point, *current_end)
                elif self.current_algorithm == 'dda':
                    points = self.dda_algorithm(*self.start_point, *current_end)
                elif self.current_algorithm == 'bresenham':
                    points = self.bresenham_algorithm(*self.start_point, *current_end)
                elif self.current_algorithm == 'circle':
                    points = self.bresenham_circle(*self.start_point, *current_end)
                elif self.current_algorithm == 'castle':
                    points = self.castle_pitway_algorithm(*self.start_point, *current_end)
                elif self.current_algorithm == 'smooth':
                    points = self.wu_line_algorithm(*self.start_point, *current_end)

                for point in points:
                    self.draw_pixel(point)

                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1_000_000
                self.execution_time = execution_time

                time_text = self.font.render(f"Time: {self.execution_time:.2f} µs", True, TEXT_COLOR)
                self.screen.blit(time_text, (200, HEIGHT - 30))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == '__main__':
    app = RasterizationApp()
    app.run()