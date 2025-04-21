import pygame
from game.pieces import General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier
from utils.const import BOARD_ROWS, BOARD_COLS, COLOR_BLACK, COLOR_RED, TYPE_GENERAL
from game.rules import validate_move, is_check_condition, set_valid_moves, remove_piece_from_board, place_piece_on_board

class Board:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.general_positions = {
            COLOR_BLACK: (0, 4),  # Vị trí ban đầu của Tướng đen
            COLOR_RED: (9, 4)     # Vị trí ban đầu của Tướng đỏ
        }
        self.simulator_pieces = None
        self.black_pieces = []  # Danh sách các quân cờ màu đen
        self.red_pieces = []    # Danh sách các quân cờ màu đỏ

    def initialize_board(self):
        """
        Khởi tạo bàn cờ tướng với các quân cờ ở vị trí ban đầu.
        """
        place_piece_on_board(self, Soldier(COLOR_BLACK), (3, 4))
        place_piece_on_board(self, General(COLOR_BLACK), (0, 4))
        place_piece_on_board(self, General(COLOR_RED), (9, 4))
        # Quân đen
        
        place_piece_on_board(self, Chariot(COLOR_BLACK), (0, 0)) 
        place_piece_on_board(self, Horse(COLOR_BLACK), (0, 1))
        place_piece_on_board(self, Elephant(COLOR_BLACK), (0, 2))
        place_piece_on_board(self, Advisor(COLOR_BLACK), (0, 3))
        place_piece_on_board(self, Advisor(COLOR_BLACK), (0, 5))
        place_piece_on_board(self, Elephant(COLOR_BLACK), (0, 6))
        place_piece_on_board(self, Horse(COLOR_BLACK), (0, 7))
        place_piece_on_board(self, Chariot(COLOR_BLACK), (0, 8))
        place_piece_on_board(self, Cannon(COLOR_BLACK), (2, 1))
        place_piece_on_board(self, Cannon(COLOR_BLACK), (2, 7))
        place_piece_on_board(self, Soldier(COLOR_BLACK), (3, 0))
        place_piece_on_board(self, Soldier(COLOR_BLACK), (3, 2))
        place_piece_on_board(self, Soldier(COLOR_BLACK), (3, 6))
        place_piece_on_board(self, Soldier(COLOR_BLACK), (3, 8))

        # Quân đỏ
        place_piece_on_board(self, Chariot(COLOR_RED), (9, 0)) 
        place_piece_on_board(self, Horse(COLOR_RED), (9, 1))
        place_piece_on_board(self, Elephant(COLOR_RED), (9, 2)) 
        place_piece_on_board(self, Advisor(COLOR_RED), (9, 3))
        place_piece_on_board(self, Advisor(COLOR_RED), (9, 5))
        place_piece_on_board(self, Elephant(COLOR_RED), (9, 6))
        place_piece_on_board(self, Horse(COLOR_RED), (9, 7))
        place_piece_on_board(self, Chariot(COLOR_RED), (9, 8))
        place_piece_on_board(self, Cannon(COLOR_RED), (7, 1))
        place_piece_on_board(self, Cannon(COLOR_RED), (7, 7))
        place_piece_on_board(self, Soldier(COLOR_RED), (6, 0))
        place_piece_on_board(self, Soldier(COLOR_RED), (6, 2))
        place_piece_on_board(self, Soldier(COLOR_RED), (6, 4))
        place_piece_on_board(self, Soldier(COLOR_RED), (6, 6))
        place_piece_on_board(self, Soldier(COLOR_RED), (6, 8))

    def is_checkmate(self, color):
        """
        Kiểm tra xem bên nào bị chiếu hết hay không.
        :param color: Màu sắc của quân cờ (COLOR_BLACK hoặc COLOR_RED)
        :return: True nếu bị chiếu hết, False nếu không
        """
        if is_check_condition(self, color):
            pieces = self.get_pieces_by_color(color)
            for piece in pieces:
                # Lấy danh sách nước đi hợp lệ của quân cờ
                valid_moves = piece.valid_positions.copy()
                current_pos = piece.current_position
                for move in valid_moves:
                    valid = self.simulator_move(current_pos, move)
                    self.undo_simulator_move(current_pos, move)
                    if valid:
                        return False
            return True
        return False
    def is_stalemate(self, color):
        """
        Kiểm tra xem bên nào bị cờ hòa hay không.
        :param color: Màu sắc của quân cờ (COLOR_BLACK hoặc COLOR_RED)
        :return: True nếu bị cờ hòa, False nếu không
        """
        pieces = self.get_pieces_by_color(color)
        for piece in pieces:
            # Lấy danh sách nước đi hợp lệ của quân cờ
            valid_moves = piece.valid_positions.copy()
            current_pos = piece.current_position
            for move in valid_moves:
                valid = self.simulator_move(current_pos, move)
                self.undo_simulator_move(current_pos, move)
                if valid:
                    return False
        return True
    
    def is_check(self, color):
        """
        Kiểm tra xem bên nào đang bị chiếu hay không.
        :param color: Màu sắc của quân cờ (COLOR_BLACK hoặc COLOR_RED)
        :return: True nếu bị chiếu, False nếu không
        """
        return is_check_condition(self, color)

    def simulator_move(self, start_pos, end_pos):
        """
        Giả lập di chuyển quân cờ từ start_pos đến end_pos.
        :param start_pos: Tuple (row, col) của vị trí bắt đầu.
        :param end_pos: Tuple (row, col) của vị trí kết thúc.
        :return: True nếu nước đi hợp lệ, False nếu không hợp lệ.
        """
        # Kiểm tra xem vị trí bắt đầu khác none không
        if start_pos is None or end_pos is None:
            return False
        # Kiểm tra xem vị trí bắt đầu và kết thúc có hợp lệ không
        if not (0 <= start_pos[0] < BOARD_ROWS and 0 <= start_pos[1] < BOARD_COLS and
                0 <= end_pos[0] < BOARD_ROWS and 0 <= end_pos[1] < BOARD_COLS):
            return False

        # Kiểm tra xem vị trí bắt đầu và kết thúc có giống nhau không
        if start_pos == end_pos:
            return False
        
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Lấy quân cờ tại vị trí bắt đầu
        piece = self.get_piece_at(start_row, start_col)
        if piece is None:
            return False  # Không có quân cờ để di chuyển

        # Kiểm tra tính hợp lệ của nước đi
        if not validate_move(start_pos, end_pos, self):
            return False  # Nước đi không hợp lệ

        # Lấy quân cờ tại vị trí kết thúc
        self.simulator_pieces = self.get_piece_at(end_row, end_col)
        # Di chuyển quân cờ
        remove_piece_from_board(self, (start_row, start_col))  # Xóa quân cờ tại vị trí bắt đầu
        place_piece_on_board(self, piece, (end_row, end_col))  # Đặt quân cờ vào vị trí mới
        # Kiểm tra xem nước đi có khiến bên mình bị chiếu không
        return is_check_condition(self, piece.color)
    
    def undo_simulator_move(self, start_pos, end_pos):
        if self.simulator_pieces is not None:
            end_row, end_col = end_pos
            # Lấy quân cờ tại vị trí bắt đầu
            piece = self.get_piece_at(end_row, end_col)
            remove_piece_from_board(self, end_pos)
            place_piece_on_board(self, piece, start_pos)
            # Đặt lại quân cờ tại vị trí cũ
            place_piece_on_board(self, self.simulator_pieces, end_pos)
            self.simulator_pieces = None

    def would_be_check(self, start_pos, end_pos, color):
        """Kiểm tra nếu di chuyển này sẽ gây chiếu tướng"""
        # Lưu trạng thái hiện tại
        moving_piece = self.get_piece_at(*start_pos)
        captured_piece = self.get_piece_at(*end_pos)
        
        # Giả lập nước đi
        self.board[end_pos[0]][end_pos[1]] = moving_piece
        self.board[start_pos[0]][start_pos[1]] = None
        if moving_piece:
            moving_piece.current_position = end_pos
        
        # Kiểm tra chiếu tướng
        result = self.is_check(color)
        
        # Hoàn tác nước đi
        self.board[start_pos[0]][start_pos[1]] = moving_piece
        self.board[end_pos[0]][end_pos[1]] = captured_piece
        if moving_piece:
            moving_piece.current_position = start_pos
        
        return result
    def move_piece(self, start_pos, end_pos):
        """
        Di chuyển quân cờ từ start_pos đến end_pos nếu hợp lệ.
        Nếu nước đi khiến bên mình bị chiếu, undo nước đi.
        :param start_pos: Tuple (row, col) của vị trí bắt đầu.
        :param end_pos: Tuple (row, col) của vị trí kết thúc.
        :return: True nếu nước đi hợp lệ, False nếu không hợp lệ.
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Lấy quân cờ tại vị trí bắt đầu
        piece = self.get_piece_at(start_row, start_col)
        if piece is None:
            return False  # Không có quân cờ để di chuyển

        # Kiểm tra tính hợp lệ của nước đi
        if not validate_move(start_pos, end_pos, self):
            return False  # Nước đi không hợp lệ

        # Lấy quân cờ tại vị trí kết thúc
        target_piece = self.get_piece_at(end_row, end_col)
        # Di chuyển quân cờ
        remove_piece_from_board(self, (start_row, start_col))  # Xóa quân cờ tại vị trí bắt đầu
        place_piece_on_board(self, piece, (end_row, end_col))  # Đặt quân cờ vào vị trí mới

        # Kiểm tra xem nước đi có khiến bên mình bị chiếu không
        if is_check_condition(self, piece.color):
            # Undo nước đi nếu bị chiếu
            remove_piece_from_board(self, (end_row, end_col))
            place_piece_on_board(self, piece, (start_row, start_col))
            # Đặt lại quân cờ tại vị trí cũ
            if target_piece:
                place_piece_on_board(self, target_piece, (end_row, end_col))
            return False
        if piece.type == TYPE_GENERAL:
            # Cập nhật vị trí của quân Tướng
            self.general_positions[piece.color] = (end_row, end_col)
        return True

    def get_general_position(self, color):
        """
        Trả về vị trí của quân Tướng (General) dựa trên màu sắc.
        :param color: COLOR_BLACK hoặc COLOR_RED
        :return: Tuple (row, col) của vị trí quân Tướng
        """
        return self.general_positions.get(color)
    
    def get_piece_at(self, row, col):
        """
        Trả về quân cờ tại vị trí (row, col).
        :param row: Hàng (row) của vị trí
        :param col: Cột (col) của vị trí
        :return: Quân cờ tại vị trí (row, col), hoặc None nếu không có quân cờ
        """
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return self.board[row][col]
        return None
    def get_pieces_by_color(self, color):
        """
        Trả về danh sách quân cờ theo màu sắc.
        :param color: Màu sắc của quân cờ (COLOR_BLACK hoặc COLOR_RED)
        :return: Danh sách quân cờ theo màu sắc
        """
        if color == COLOR_BLACK:
            return self.black_pieces
        elif color == COLOR_RED:
            return self.red_pieces
        return []
    def get_all_pieces(self):
        """
        Trả về danh sách tất cả các quân cờ trên bàn cờ.
        :return: Danh sách tất cả các quân cờ
        """
        all_pieces = self.black_pieces + self.red_pieces
        return all_pieces