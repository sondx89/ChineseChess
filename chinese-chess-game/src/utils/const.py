# --- Screen Dimensions ---
SCREEN_WIDTH = 1100  # Tăng thêm chiều rộng để hiển thị quân bị ăn
SCREEN_HEIGHT = 850
STATUS_BAR_HEIGHT = 40

# --- Board Dimensions ---
BOARD_ROWS, BOARD_COLS = 10, 9
SQUARE_SIZE = 60
BOARD_WIDTH = (BOARD_COLS - 1) * SQUARE_SIZE
BOARD_HEIGHT = (BOARD_ROWS - 1) * SQUARE_SIZE
BOARD_LEFT_MARGIN = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP_MARGIN = 100  # Khoảng cách từ đỉnh màn hình

# --- Colors ---
# Màu nền
BACKGROUND_COLOR = (240, 240, 220)  # Màu be nhạt
BOARD_COLOR = (222, 184, 135)  # Màu nâu nhạt cho bàn cờ
LINE_COLOR = (50, 50, 50)  # Màu đen cho đường kẻ
RIVER_COLOR = (173, 216, 230, 150)  # Màu xanh nước biển nhạt cho sông
HIGHLIGHT_COLOR = (50, 205, 50, 180)  # Màu xanh lá cây trong suốt cho highlight

# Màu chữ
TEXT_COLOR = (50, 50, 50)
TEXT_WHITE = (255, 255, 255)
TEXT_GOLD = (255, 215, 0)

# --- Font Settings ---
FONT_NAME = "Arial"  # Sử dụng font Arial hỗ trợ tiếng Việt tốt
TITLE_FONT_SIZE = 48
SUBTITLE_FONT_SIZE = 24
STATUS_FONT_SIZE = 20
CAPTURED_FONT_SIZE = 18

# --- Game Elements ---
# Palaces
BLACK_PALACE = {"row_min": 0, "row_max": 2, "col_min": 3, "col_max": 5}
RED_PALACE = {"row_min": 7, "row_max": 9, "col_min": 3, "col_max": 5}

# River
RIVER_ROW_TOP = 4
RIVER_ROW_BOTTOM = 5

# --- Piece Settings ---
PIECE_SCALE = 0.8  # Tỉ lệ quân cờ so với ô vuông
HIGHLIGHT_CIRCLE_RADIUS = int(SQUARE_SIZE * PIECE_SCALE / 2)

# --- Player Colors ---
COLOR_BLACK = "black"
COLOR_RED = "red"
COLOR_NONE = "none"

# --- Piece Types ---
TYPE_GENERAL = "general"
TYPE_ADVISOR = "advisor"
TYPE_ELEPHANT = "elephant"
TYPE_HORSE = "horse"
TYPE_CHARIOT = "chariot"
TYPE_CANNON = "cannon"
TYPE_SOLDIER = "soldier"