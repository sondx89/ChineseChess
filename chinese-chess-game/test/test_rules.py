import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from game.rules import (
    set_valid_moves,_count_pieces_between,
    place_piece_on_board, remove_piece_from_board
)
from game.pieces import General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier
from utils.const import COLOR_BLACK, COLOR_RED, BOARD_ROWS, BOARD_COLS
from game.board import Board  # Import class Board

class TestRules(unittest.TestCase):
    def setUp(self):
        """
        Thiết lập bàn cờ và các quân cờ để sử dụng trong các bài test.
        """
        self.board = Board()  # Khởi tạo đối tượng Board

        # Khởi tạo các quân cờ
        self.general_black = General(COLOR_BLACK)
        self.general_red = General(COLOR_RED)
        self.advisor_black = Advisor(COLOR_BLACK)
        self.elephant_black = Elephant(COLOR_BLACK)
        self.horse_black = Horse(COLOR_BLACK)
        self.chariot_black = Chariot(COLOR_BLACK)
        self.cannon_black = Cannon(COLOR_BLACK)
        self.soldier_black = Soldier(COLOR_BLACK)

    def tearDown(self):
        """
        Dọn dẹp bàn cờ sau mỗi test case để đảm bảo tính độc lập.
        """
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

    def test_set_valid_moves_general(self):
        """
        Test hàm set_valid_moves cho quân Tướng khi ở giữa cung và đối diện Tướng đối phương.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Tướng đen vào giữa cung (1, 4)
        place_piece_on_board(self.board, self.general_black, (1, 4))
        # Đặt Tướng đỏ vào vị trí mép cung (9, 4)
        place_piece_on_board(self.board, self.general_red, (9, 4))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Tướng đen
        set_valid_moves(self.general_black, self.board)

        # 3. Kiểm tra:
        # Tướng có thể di chuyển đến (1, 3)
        self.assertIn((1, 3), self.general_black.valid_positions)
        # Tướng có thể di chuyển đến (0, 4)
        self.assertIn((0, 4), self.general_black.valid_positions)
        # Tướng có thể di chuyển đến (1, 5)
        self.assertIn((1, 5), self.general_black.valid_positions)
        # Tướng không thể di chuyển đến (2, 4) vì sẽ đối mặt với tướng đỏ
        self.assertNotIn((2, 4), self.general_black.valid_positions)

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (1, 4))
        remove_piece_from_board(self.board, (9, 4))

    def test_set_valid_moves_advisor(self):
        """
        Test hàm set_valid_moves cho quân Sĩ khi ở giữa cung.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Sĩ đen vào giữa cung (1, 4)
        place_piece_on_board(self.board, self.advisor_black, (1, 4))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Sĩ đen
        set_valid_moves(self.advisor_black, self.board)

        # 3. Kiểm tra:
        # Sĩ có thể di chuyển đến (0, 3)
        self.assertIn((0, 3), self.advisor_black.valid_positions)
        # Sĩ có thể di chuyển đến (0, 5)
        self.assertIn((0, 5), self.advisor_black.valid_positions)
        # Sĩ có thể di chuyển đến (2, 3)
        self.assertIn((2, 3), self.advisor_black.valid_positions)
        # Sĩ có thể di chuyển đến (2, 5)
        self.assertIn((2, 5), self.advisor_black.valid_positions)

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (1, 4))

    def test_set_valid_moves_elephant(self):
        """
        Test hàm set_valid_moves cho quân Tượng.
        Kiểm tra tượng không được qua sông và bị chặn ở mắt.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Tượng đen vào vị trí (2, 2)
        place_piece_on_board(self.board, self.elephant_black, (2, 2))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Tượng đen
        set_valid_moves(self.elephant_black, self.board)

        # 3. Kiểm tra:
        # Tượng có thể di chuyển đến (0, 0)
        self.assertIn((0, 0), self.elephant_black.valid_positions)
        # Tượng có thể di chuyển đến (0, 4)
        self.assertIn((0, 4), self.elephant_black.valid_positions)
        # Tượng không thể di chuyển đến (4, 0) vì qua sông
        self.assertNotIn((4, 0), self.elephant_black.valid_positions)
        # Tượng không thể di chuyển đến (4, 4) vì qua sông
        self.assertNotIn((4, 4), self.elephant_black.valid_positions)

        # Kiểm tra bị chặn ở mắt
        block_piece = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece, (1, 1))
        set_valid_moves(self.elephant_black, self.board)
        self.assertNotIn((0, 0), self.elephant_black.valid_positions)  # Bị chặn ở mắt

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (1, 1))

    def test_set_valid_moves_horse(self):
        """
        Test hàm set_valid_moves cho quân Mã.
        Kiểm tra mã bị chặn bởi quân cản.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Mã đen vào vị trí giữa bàn cờ (4, 4)
        place_piece_on_board(self.board, self.horse_black, (4, 4))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Mã đen
        set_valid_moves(self.horse_black, self.board)

        # 3. Kiểm tra:
        # Mã có thể di chuyển đến (2, 3)
        self.assertIn((2, 3), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (2, 5)
        self.assertIn((2, 5), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (3, 2)
        self.assertIn((3, 2), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (3, 6)
        self.assertIn((3, 6), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (5, 2)
        self.assertIn((5, 2), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (5, 6)
        self.assertIn((5, 6), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (6, 3)
        self.assertIn((6, 3), self.horse_black.valid_positions)
        # Mã có thể di chuyển đến (6, 5)
        self.assertIn((6, 5), self.horse_black.valid_positions)

        # Đặt quân cản ở "chân" Mã
        block_piece = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece, (4, 3))
        set_valid_moves(self.horse_black, self.board)
        self.assertNotIn((3, 2), self.horse_black.valid_positions)  # Bị chặn
        self.assertIn((6, 3), self.horse_black.valid_positions)  # Không bị chặn

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (4, 3))

    def test_set_valid_moves_chariot(self):
        """
        Test hàm set_valid_moves cho quân Xe.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Xe đen vào vị trí giữa bàn cờ (5, 4)
        place_piece_on_board(self.board, self.chariot_black, (5, 4))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Xe đen
        set_valid_moves(self.chariot_black, self.board)

        # 3. Kiểm tra:
        # Kiểm tra các nước đi hợp lệ theo hàng và cột
        self.assertIn((5, 0), self.chariot_black.valid_positions)
        self.assertIn((5, 8), self.chariot_black.valid_positions)
        self.assertIn((0, 4), self.chariot_black.valid_positions)
        self.assertIn((9, 4), self.chariot_black.valid_positions)

        # Đặt vật cản tại hàng của quân xe
        block_piece1 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece1, (5, 2))
        set_valid_moves(self.chariot_black, self.board)
        self.assertNotIn((5, 1), self.chariot_black.valid_positions)
        self.assertNotIn((5, 0), self.chariot_black.valid_positions)
        self.assertIn((5, 3), self.chariot_black.valid_positions)

        # Đặt thêm 1 vật cản ở cùng hàng với quân xe và vật cản 1, ở giữa quân xe và vật cản 1
        block_piece2 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece2, (5, 3))
        set_valid_moves(self.chariot_black, self.board)
        self.assertNotIn((5, 4), self.chariot_black.valid_positions)
        self.assertIn((5, 5), self.chariot_black.valid_positions)

        # Đặt thêm 1 vật cản ở cùng hàng với quân xe và vật cản 1, ở ngoài quân xe và vật cản 1
        block_piece3 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece3, (5, 6))
        set_valid_moves(self.chariot_black, self.board)
        self.assertIn((5, 5), self.chariot_black.valid_positions)
        self.assertNotIn((5, 7), self.chariot_black.valid_positions)

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (5, 2))
        remove_piece_from_board(self.board, (5, 3))
        remove_piece_from_board(self.board, (5, 6))

    def test_set_valid_moves_cannon(self):
        """
        Test hàm set_valid_moves cho quân Pháo.
        Kiểm tra pháo có thể ăn cách quân.
        """
        # 1. Thiết lập:
        # Loại bỏ tất cả các quân cờ khỏi bàn cờ
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board.board[row][col] is not None:
                    remove_piece_from_board(self.board, (row, col))

        # Đặt Pháo đen vào vị trí giữa bàn cờ (5, 4)
        place_piece_on_board(self.board, self.cannon_black, (5, 4))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Pháo đen
        set_valid_moves(self.cannon_black, self.board)

        # 3. Kiểm tra:
        # Kiểm tra các nước đi hợp lệ theo hàng và cột khi không có vật cản
        self.assertIn((5, 0), self.cannon_black.valid_positions)
        self.assertIn((5, 8), self.cannon_black.valid_positions)
        self.assertIn((0, 4), self.cannon_black.valid_positions)
        self.assertIn((9, 4), self.cannon_black.valid_positions)

        # Đặt vật cản tại hàng của quân Pháo
        block_piece1 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece1, (5, 2))
        set_valid_moves(self.cannon_black, self.board)
        self.assertNotIn((5, 1), self.cannon_black.valid_positions)
        self.assertNotIn((5, 0), self.cannon_black.valid_positions)
        self.assertIn((5, 3), self.cannon_black.valid_positions)

        # Đặt thêm 1 vật cản ở cùng hàng với quân Pháo và vật cản 1, ở giữa quân Pháo và vật cản 1
        block_piece2 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece2, (5, 3))
        set_valid_moves(self.cannon_black, self.board)
        self.assertNotIn((5, 4), self.cannon_black.valid_positions)
        self.assertIn((5, 5), self.cannon_black.valid_positions)

        # Đặt thêm 1 vật cản ở cùng hàng với quân Pháo và vật cản 1, ở ngoài quân Pháo và vật cản 1
        block_piece3 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, block_piece3, (5, 6))
        set_valid_moves(self.cannon_black, self.board)
        self.assertIn((5, 5), self.cannon_black.valid_positions)
        self.assertNotIn((5, 7), self.cannon_black.valid_positions)

        # Đặt quân để pháo ăn
        target_piece = Soldier(COLOR_RED)
        place_piece_on_board(self.board, target_piece, (5, 7))
        set_valid_moves(self.cannon_black, self.board)
        self.assertIn((5, 7), self.cannon_black.valid_positions)

        # Dọn dẹp: Loại bỏ các quân cờ đã được đặt vào bàn cờ
        remove_piece_from_board(self.board, (5, 2))
        remove_piece_from_board(self.board, (5, 3))
        remove_piece_from_board(self.board, (5, 6))
        remove_piece_from_board(self.board, (5, 7))

    def test_set_valid_moves_soldier(self):
        """
        Test hàm set_valid_moves cho quân Tốt.
        Kiểm tra tốt sau khi qua sông.
        """
        # 1. Thiết lập: Đặt Tốt đen vào vị trí (6, 0)
        place_piece_on_board(self.board, self.soldier_black, (6, 0))

        # 2. Thực hiện: Tính toán các nước đi hợp lệ cho Tốt đen
        set_valid_moves(self.soldier_black, self.board)

        # 3. Kiểm tra:
        # Tốt có thể đi thẳng
        self.assertIn((7, 0), self.soldier_black.valid_positions)

        # Sau khi qua sông, tốt có thể đi ngang
        remove_piece_from_board(self.board, (6, 0))
        place_piece_on_board(self.board, self.soldier_black, (5, 0))
        set_valid_moves(self.soldier_black, self.board)
        self.assertIn((5, 1), self.soldier_black.valid_positions)
        self.assertIn((6, 0), self.soldier_black.valid_positions)
        remove_piece_from_board(self.board, (5, 0))

    def test_count_pieces_between(self):
        """
        Test hàm _count_pieces_between để đếm số quân cờ giữa hai vị trí.
        """
        # 1. Thiết lập: Đặt hai quân cờ vào vị trí (1, 4) và (2, 4)
        piece1 = Soldier(COLOR_BLACK)
        piece2 = Soldier(COLOR_BLACK)
        place_piece_on_board(self.board, piece1, (1, 4))
        place_piece_on_board(self.board, piece2, (2, 4))

        # 2. Thực hiện: Đếm số quân cờ giữa (0, 4) và (3, 4)
        count = _count_pieces_between((0, 4), (3, 4), self.board.board)

        # 3. Kiểm tra: Số quân cờ giữa (0, 4) và (3, 4) là 2
        self.assertEqual(count, 2)
        remove_piece_from_board(self.board, (1, 4))
        remove_piece_from_board(self.board, (2, 4))

if __name__ == "__main__":
    unittest.main()