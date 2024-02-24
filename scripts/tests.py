import unittest

from maze import Maze, Window

class Tests(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.num_cols = 12
        self.num_rows = 10
        self.m1 = Maze(0,0,self.num_rows,self.num_cols, 10, 10, None)

    def test_maze_create_cells(self):
        self.assertEqual(len(self.m1._cells), self.num_cols)
        self.assertEqual(len(self.m1._cells[0]), self.num_rows)

    def test_maze_clears_entrance_and_exit(self):
        self.assertEqual(self.m1._cells[0][0].right_wall, True)
        self.assertEqual(self.m1._cells[-1][-1].right_wall, True)
        self.m1._break_entrance_and_exit()
        self.assertEqual(self.m1._cells[0][0].right_wall, False)
        self.assertEqual(self.m1._cells[-1][-1].right_wall, False)

    def test_maze_clears_visited(self):
        maze = Maze(10,10,self.num_rows,self.num_cols, 10, 10, None, speed=0.0)
        self.assertEqual(maze._cells[0][0].visited, False)
        maze._break_walls_r(0,0)
        self.assertEqual(maze._cells[0][0].visited, True)
        maze._reset_cells_visited()
        self.assertEqual(maze._cells[0][0].visited, False)

    def test_empty_maze_exception(self):
        self.assertRaises(Exception,lambda o: Maze(0, 0, 0, 0, 0, 0, None),
                          msg='There must be at least 1 column and row')

    def test_run_render(self):
        win = Window(500, 500)
        maze = Maze(10,10,self.num_rows,self.num_cols, 10, 10, win)
        self.m1 = maze
        maze.break_walls()
        maze.solve()
        win.wait_for_close()


if __name__ == "__main__":
    unittest.main()