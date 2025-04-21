import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from game.pieces import General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier
from utils.const import BOARD_ROWS, BOARD_COLS, BLACK_PALACE, RED_PALACE, RIVER_ROW_TOP, RIVER_ROW_BOTTOM

class TestPieces(unittest.TestCase):
    def setUp(self):
        # Tạo bàn cờ trống
        self.empty_board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

    def test_general_moves(self):
        general = General("black")
        general.set_position((1, 4))
        expected_moves = [(0, 4), (2, 4), (1, 3), (1, 5)]
        self.assertCountEqual(general.can_moves, expected_moves)

    def test_advisor_moves(self):
        advisor = Advisor("red")
        advisor.set_position((8, 4))
        expected_moves = [(7, 3), (7, 5), (9, 3), (9, 5)]
        self.assertCountEqual(advisor.can_moves, expected_moves)

    def test_elephant_moves(self):
        elephant = Elephant("black")
        elephant.set_position((2, 2))
        expected_moves = [(0, 0), (0, 4), (4, 0), (4, 4)]
        self.assertCountEqual(elephant.can_moves, expected_moves)

    def test_horse_moves(self):
        horse = Horse("red")
        horse.set_position((4, 4))
        expected_moves = [(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)]
        self.assertCountEqual(horse.can_moves, expected_moves)

    def test_chariot_moves(self):
        chariot = Chariot("black")
        chariot.set_position((4, 4))
        expected_moves = [(4, c) for c in range(BOARD_COLS) if c != 4] + [(r, 4) for r in range(BOARD_ROWS) if r != 4]
        self.assertCountEqual(chariot.can_moves, expected_moves)

    def test_cannon_moves(self):
        cannon = Cannon("red")
        cannon.set_position((4, 4))
        expected_moves = [(4, c) for c in range(BOARD_COLS) if c != 4] + [(r, 4) for r in range(BOARD_ROWS) if r != 4]
        self.assertCountEqual(cannon.can_moves, expected_moves)

    def test_soldier_moves(self):
        # Trường hợp quân đen trước khi qua sông
        soldier_black = Soldier("black")
        soldier_black.set_position((4, 4))  # Quân đen ở vị trí (4, 4)
        expected_moves = [(5, 4)]  # Chỉ đi thẳng xuống
        self.assertCountEqual(soldier_black.can_moves, expected_moves)

        # Trường hợp quân đen sau khi qua sông
        soldier_black.set_position((5, 4))  # Quân đen ở vị trí (5, 4)
        expected_moves = [(6, 4), (5, 3), (5, 5)]  # Đi thẳng xuống và đi ngang
        self.assertCountEqual(soldier_black.can_moves, expected_moves)

        # Trường hợp quân đỏ trước khi qua sông
        soldier_red = Soldier("red")
        soldier_red.set_position((5, 4))  # Quân đỏ ở vị trí (5, 4)
        expected_moves = [(4, 4)]  # Chỉ đi thẳng lên
        self.assertCountEqual(soldier_red.can_moves, expected_moves)

        # Trường hợp quân đỏ sau khi qua sông
        soldier_red.set_position((4, 4))  # Quân đỏ ở vị trí (4, 4)
        expected_moves = [(3, 4), (4, 3), (4, 5)]  # Đi thẳng lên và đi ngang
        self.assertCountEqual(soldier_red.can_moves, expected_moves)

if __name__ == "__main__":
    unittest.main()