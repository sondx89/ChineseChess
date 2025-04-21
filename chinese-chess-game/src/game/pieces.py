import os
from utils.const import (
    BLACK_PALACE, RED_PALACE, RIVER_ROW_TOP, RIVER_ROW_BOTTOM, BOARD_ROWS, BOARD_COLS,
    COLOR_BLACK, COLOR_RED, COLOR_NONE,
    TYPE_GENERAL, TYPE_ADVISOR, TYPE_ELEPHANT, TYPE_HORSE, TYPE_CHARIOT, TYPE_CANNON, TYPE_SOLDIER
)

class Piece:
    def __init__(self, color):
        self.color = color
        self.name = None
        self.type = None  # Loại quân cờ (ví dụ: "general", "advisor", "elephant", ...)
        self.image_path = None
        self.current_position = None  # Vị trí hiện tại của quân cờ
        self.valid_positions = []  # Danh sách các vị trí có thể di chuyển đến  
        self.can_moves = []  # Danh sách các vị trí có thể di chuyển đến

    def __eq__(self, other):
        """
        So sánh hai quân cờ dựa trên vị trí hiện tại.
        """
        if isinstance(other, Piece):
            return self.current_position == other.current_position
        return False

    def __hash__(self):
        """
        Tạo hash dựa trên vị trí hiện tại để sử dụng trong các cấu trúc dữ liệu như set hoặc dict.
        """
        return hash(self.current_position)
    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân cờ.
        Phương thức này sẽ được ghi đè trong các lớp con.
        """
        raise NotImplementedError("Phương thức này cần được ghi đè trong lớp con.")
    def set_position(self, position):
        """
        Thiết lập vị trí hiện tại của quân cờ.
        :param position: Tuple (row, col) của vị trí
        """
        self.current_position = position
        self._calculate_can_moves()
    
class General(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_general"
        self.type = TYPE_GENERAL  # Sử dụng hằng số TYPE_GENERAL
        self.image_path = os.path.join("images", f"{color[0]}G.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Tướng (General).
        Quân Tướng chỉ có thể đi 1 ô theo chiều ngang hoặc dọc trong cung (palace).
        Không được phép ra khỏi cung.
        """
        row, col = self.current_position
        self.can_moves = []
        
        # Xác định cung (palace) dựa vào màu quân
        if self.color == COLOR_BLACK:
            palace = BLACK_PALACE
        else:  # COLOR_RED
            palace = RED_PALACE
        
        # Các hướng di chuyển có thể (lên, xuống, trái, phải)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra xem vị trí mới có nằm trong cung không
            if (palace["row_min"] <= new_row <= palace["row_max"] and
                palace["col_min"] <= new_col <= palace["col_max"]):
                self.can_moves.append((new_row, new_col))

class Advisor(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_advisor"
        self.type = TYPE_ADVISOR  # Sử dụng hằng số TYPE_ADVISOR
        self.image_path = os.path.join("images", f"{color[0]}A.png")
    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Sĩ (Advisor).
        Quân Sĩ chỉ được đi 1 ô chéo trong cung (palace), không đi ngang/dọc.
        """
        row, col = self.current_position
        self.can_moves = []
        
        # Xác định cung (palace) dựa vào màu quân
        if self.color == COLOR_BLACK:
            palace = BLACK_PALACE
        else:  # COLOR_RED
            palace = RED_PALACE
        
        # Các hướng di chuyển chéo có thể (4 hướng chéo)
        diagonal_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in diagonal_moves:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra xem vị trí mới có nằm trong cung không
            if (palace["row_min"] <= new_row <= palace["row_max"] and
                palace["col_min"] <= new_col <= palace["col_max"]):
                self.can_moves.append((new_row, new_col))

class Elephant(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_elephant"
        self.type = TYPE_ELEPHANT  # Sử dụng hằng số TYPE_ELEPHANT
        self.image_path = os.path.join("images", f"{color[0]}E.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Tượng (Elephant).
        - Đi 2 ô chéo (kiểu "田").
        - Không vượt sông (chỉ hoạt động bên phần sân nhà).
        - Bị cản nếu có quân nằm ở ô giữa.
        """
        row, col = self.current_position
        self.can_moves = []

        # Xác định phạm vi sân nhà (không vượt sông)
        # Xác định khu vực mà Tượng có thể di chuyển (nửa bàn cờ của mỗi bên)
        if self.color == COLOR_BLACK:
            min_row = 0
            max_row = RIVER_ROW_TOP  # Tượng đen không được vượt qua sông
        else:
            min_row = RIVER_ROW_BOTTOM  # Tượng đỏ không được vượt qua sông
            max_row = BOARD_ROWS - 1

        # Kiểm tra các hướng di chuyển
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            new_row, new_col = row + dr, col + dc
            # Kiểm tra xem vị trí mới có nằm trên bàn cờ và trong khu vực của Tượng không
            if min_row <= new_row <= max_row and 0 <= new_col < BOARD_COLS:
                self.can_moves.append((new_row, new_col))

class Horse(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_horse"
        self.type = TYPE_HORSE
        self.image_path = os.path.join("images", f"{color[0]}H.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Mã (Knight)
        với giả định KHÔNG bị cản chân (không kiểm tra quân chặn ở vị trí ngang/dọc kề).
        - Đi theo hình chữ "NHẬT" (1 ô ngang/dọc + 1 ô chéo).
        - Không kiểm tra điều kiện "cản mã".
        """
        row, col = self.current_position
        self.can_moves = []

        # 8 hướng đi có thể của Mã (hình chữ NHẬT)
        moves = [
            (-2, -1), (-2, 1),  # Lên 2 ô + ngang 1 ô
            (-1, -2), (-1, 2),   # Lên 1 ô + ngang 2 ô
            (1, -2), (1, 2),     # Xuống 1 ô + ngang 2 ô
            (2, -1), (2, 1)       # Xuống 2 ô + ngang 1 ô
        ]

        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra xem có nằm trong bàn cờ không (9 cột x 10 hàng)
            if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
                self.can_moves.append((new_row, new_col))

        return self.can_moves

class Chariot(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_chariot"
        self.type = TYPE_CHARIOT  # Sử dụng hằng số TYPE_CHARIOT
        self.image_path = os.path.join("images", f"{color[0]}R.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Xe (Rook) 
        trong điều kiện KHÔNG bị chặn bởi bất kỳ quân nào.
        - Đi ngang/dọc không giới hạn ô.
        - Không kiểm tra quân cản, có thể "đi xuyên" qua mọi quân.
        """
        row, col = self.current_position
        self.can_moves = []
        
        # Tất cả các ô cùng hàng (ngang)
        for c in range(BOARD_COLS):  # Bàn cờ có 9 cột (0-8)
            if c != col:
                self.can_moves.append((row, c))
        
        # Tất cả các ô cùng cột (dọc)
        for r in range(BOARD_ROWS):  # Bàn cờ có 10 hàng (0-9)
            if r != row:
                self.can_moves.append((r, col))
        
        return self.can_moves

class Cannon(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_cannon"
        self.type = TYPE_CANNON  # Sử dụng hằng số TYPE_CANNON
        self.image_path = os.path.join("images", f"{color[0]}C.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Xe (Rook) 
        trong điều kiện KHÔNG bị chặn bởi bất kỳ quân nào.
        - Đi ngang/dọc không giới hạn ô.
        - Không kiểm tra quân cản, có thể "đi xuyên" qua mọi quân.
        """
        row, col = self.current_position
        self.can_moves = []
        
        # Tất cả các ô cùng hàng (ngang)
        for c in range(BOARD_COLS):  # Bàn cờ có 9 cột (0-8)
            if c != col:
                self.can_moves.append((row, c))
        
        # Tất cả các ô cùng cột (dọc)
        for r in range(BOARD_ROWS):  # Bàn cờ có 10 hàng (0-9)
            if r != row:
                self.can_moves.append((r, col))
        
        return self.can_moves

class Soldier(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.name = f"{color}_soldier"
        self.type = TYPE_SOLDIER  # Sử dụng hằng số TYPE_SOLDIER
        self.image_path = os.path.join("images", f"{color[0]}S.png")

    def _calculate_can_moves(self):
        """
        Tính toán các vị trí có thể di chuyển của quân Tốt (Soldier/Pawn)
        - Chưa qua sông: Chỉ được tiến 1 ô thẳng
        - Đã qua sông: Được tiến/lui 1 ô thẳng hoặc đi ngang 1 ô
        - Không kiểm tra quân cản (vì Tốt ăn quân đối phương theo cách di chuyển)
        """
        row, col = self.current_position
        self.can_moves = []

        if self.color == COLOR_BLACK:  # Quân đen (đi từ trên xuống)
            # Tiến 1 ô (xuống dưới)
            if row + 1 < BOARD_ROWS:  # Kiểm tra biên dưới
                self.can_moves.append((row + 1, col))
            
            # Nếu đã qua sông (row >= 5) thì được đi ngang
            if row >= RIVER_ROW_BOTTOM:
                if col - 1 >= 0:  # Sang trái
                    self.can_moves.append((row, col - 1))
                if col + 1 < BOARD_COLS:  # Sang phải
                    self.can_moves.append((row, col + 1))

        else:  # Quân đỏ (đi từ dưới lên)
            # Tiến 1 ô (lên trên)
            if row - 1 >= 0:  # Kiểm tra biên trên
                self.can_moves.append((row - 1, col))
            
            # Nếu đã qua sông (row <= 4) thì được đi ngang
            if row <= RIVER_ROW_TOP:
                if col - 1 >= 0:  # Sang trái
                    self.can_moves.append((row, col - 1))
                if col + 1 < BOARD_COLS:  # Sang phải
                    self.can_moves.append((row, col + 1))

        return self.can_moves