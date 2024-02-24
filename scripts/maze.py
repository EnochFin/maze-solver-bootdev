from tkinter import Tk, BOTH, Canvas
from typing import Any
import time

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        root = Tk()
        root.title = 'Some Title'
        self.__root = root
        canvas =  Canvas(self.__root)
        canvas.pack()
        self.__canvas = canvas
        self.is_running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.is_running = True
        while(self.is_running):
            self.redraw()
    
    def close(self):
        self.is_running = False
    
    def draw_line(self, line, fill_color):
        line.draw(self.__canvas, fill_color)
        
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2

    def draw(self, canvas, fill_color):
        canvas.create_line(self.p1.x, self.p1.y, self.p2.x, self.p2.y, fill=fill_color, width=2)
        canvas.pack()

class Cell:
    # [l, r, t, b]
    def __init__(self, line, window):
        self.left_wall = True
        self.right_wall = True
        self.top_wall = True
        self.bottom_wall = True
        self._coords = line
        self._win = window

    def _wall_color(self, wall_up):
        return 'black' if wall_up else 'white'

    def draw(self):
        p1 = self._coords.p1
        p2 = self._coords.p2
        # top line
        self._win.draw_line(Line(Point(p1.x, p1.y), Point(p2.x, p1.y)), self._wall_color(self.top_wall))
        # bottom
        self._win.draw_line(Line(Point(p1.x, p2.y), Point(p2.x, p2.y)), self._wall_color(self.bottom_wall))
        # left
        self._win.draw_line(Line(Point(p1.x, p1.y), Point(p1.x, p2.y)), self._wall_color(self.left_wall))
        # right
        self._win.draw_line(Line(Point(p2.x, p1.y), Point(p2.x, p2.y)), self._wall_color(self.right_wall))

    def draw_move(self, to_cell, undo=False):
        p1 = self._coords.p1
        p2 = self._coords.p2
        my_center = Point((p1.x + p2.x) // 2, (p1.y + p2.y) // 2)
        to_center = Point((to_cell._x1 + to_cell._x2) // 2, (to_cell._y1 + to_cell._y2) // 2)
        color = 'red' if undo else 'gray'
        self._win.draw_line(Line(my_center, to_center), color)

    def clear_walls(self):
        self.top_wall = False
        self.right_wall = False
        self.bottom_wall = False
        self.left_wall = False

class Maze:
    def __init__(
            self,
            x1,
            y1,
            num_rows,
            num_cols,
            cell_size_x,
            cell_size_y,
            win
            ) :
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self._win = win
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for x in range(self.num_cols):
            curr_x_start = self.x1 + self.cell_size_x * x
            curr_x_end = self.x1 + self.cell_size_x * (x+1)
            row = []
            for y in range(self.num_rows):
                curr_y_start = self.y1 + self.cell_size_y * y
                curr_y_end = self.y1 + self.cell_size_y * (y+1)
                row += [Cell(Line(Point(curr_x_start, curr_y_start),
                                Point(curr_x_end, curr_y_end)),
                            self._win)]
            self._cells += [row]

    def _draw_cell(self, i, j):
        self._cells[i][j].draw()
        self._animate()

    def _animate(self):
        self._win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        entrance = self._cells[0][0]
        exit = self._cells[-1][-1]
        entrance.clear_walls()
        exit.clear_walls()
