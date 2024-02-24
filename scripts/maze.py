import random
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
        self.coords = line
        self._win = window
        self.visited = False

    def _wall_color(self, wall_up):
        return 'black' if wall_up else 'white'

    def draw(self):
        p1 = self.coords.p1
        p2 = self.coords.p2
        # top line
        self._win.draw_line(Line(Point(p1.x, p1.y), Point(p2.x, p1.y)), self._wall_color(self.top_wall))
        # bottom
        self._win.draw_line(Line(Point(p1.x, p2.y), Point(p2.x, p2.y)), self._wall_color(self.bottom_wall))
        # left
        self._win.draw_line(Line(Point(p1.x, p1.y), Point(p1.x, p2.y)), self._wall_color(self.left_wall))
        # right
        self._win.draw_line(Line(Point(p2.x, p1.y), Point(p2.x, p2.y)), self._wall_color(self.right_wall))

    def draw_move(self, to_cell, undo=False):
        p1 = self.coords.p1
        p2 = self.coords.p2
        to_p1 = to_cell.coords.p1
        to_p2 = to_cell.coords.p2
        my_center = Point((p1.x + p2.x) // 2, (p1.y + p2.y) // 2)
        to_center = Point((to_p1.x + to_p2.x) // 2, (to_p1.y + to_p2.y) // 2)
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
            win,
            seed = None,
            speed = 0.05,
            ) :
        if num_cols < 1 or num_rows < 1:
            raise Exception('There must be at least 1 column and row')
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self._win = win
        self._speed = speed
        self._drawing = win is not None
        if seed is not None:
            random.seed(seed)

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

    def _get_need_visit(self, i, j, visited = False):
        need_visit = []
        # check left
        if i > 0:
            if self._cells[i - 1][j].visited == visited:
                need_visit += [(i - 1, j)]
        # check right
        if i < len(self._cells) - 1:
            if self._cells[i + 1][j].visited == visited:
                need_visit += [(i + 1, j)]
        # check top
        if j > 0:
            if self._cells[i][j - 1].visited == visited:
                need_visit += [(i, j - 1)]
        # check bottom
        if j < len(self._cells[0]) - 1:
            if self._cells[i][j + 1].visited == visited:
                need_visit += [(i, j + 1)]
        return need_visit
    
    def _break_wall(self, i, j, to_i, to_j):
        curr = self._cells[i][j]
        to_cell = self._cells[to_i][to_j]
        if to_i < i:
            # left
            curr.left_wall = False
            to_cell.right_wall = False
        elif to_i > i:
            # right
            curr.right_wall = False
            to_cell.left_wall = False
        elif to_j < j:
            # top
            curr.top_wall = False
            to_cell.bottom_wall = False
        elif to_j > j:
            # bottom
            curr.bottom_wall = False
            to_cell.top_wall = False

    def _get_available_adjacent(self, i, j, adjacent):
        result = []
        curr = self._cells[i][j]
        for to_i, to_j in adjacent:
            to_cell = self._cells[to_i][to_j]
            if to_cell.visited is False:
                left = to_i < i and not curr.left_wall
                right = to_i > i and not curr.right_wall
                top = to_j < j and not curr.top_wall
                bottom = to_j > j and not curr.bottom_wall
                if left or right or top or bottom:
                    result += [(to_i, to_j, to_cell)]
        return result
    
    def break_walls(self):
        self._break_walls_r(0, 0)
        self._break_entrance_and_exit()
        self._reset_cells_visited()

    def _break_walls_r(self, i, j):
        curr = self._cells[i][j]
        curr.visited = True
        while True:
            need_visit = self._get_need_visit(i, j)
            if len(need_visit) == 0:
                if self._drawing:
                    self._draw_cell(i, j)
                return
            rand_dir = random.choice(need_visit)
            to_i = rand_dir[0]
            to_j = rand_dir[1]
            self._break_wall(i, j, to_i, to_j)
            self._break_walls_r(to_i, to_j)
    
    def solve(self):
        return self._solve_r(0, 0)
    
    def _solve_r(self, i, j):
        self._animate()
        curr = self._cells[i][j]
        curr.visited = True
        if i == len(self._cells)-1 and j == len(self._cells[0])-1:
            return True
        adjacent = self._get_need_visit(i, j)
        avail_adj = self._get_available_adjacent(i, j, adjacent)
        for to_i, to_j, adj in avail_adj:
            if self._drawing:
                curr.draw_move(adj)
            if self._solve_r(to_i, to_j):
                return True
            if self._drawing:
                curr.draw_move(adj, undo=True)
        return False


    def _draw_cell(self, i, j):
        if self._drawing:
            self._cells[i][j].draw()
            self._animate()

    def _animate(self):
        self._win.redraw()
        time.sleep(self._speed)

    def _break_entrance_and_exit(self):
        entrance = self._cells[0][0]
        ext = self._cells[-1][-1]
        entrance.clear_walls()
        ext.clear_walls()
        self._draw_cell(0,0)
        self._draw_cell(-1,-1)

    def _reset_cells_visited(self):
        for x in range(self.num_cols):
            for y in range(self.num_rows):
                self._cells[x][y].visited = False
