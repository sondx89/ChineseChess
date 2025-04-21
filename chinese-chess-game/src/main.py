import pygame
import time
from game.board import Board
from view.draw import *
from utils.const import *
from utils.ComputerPlayer import ComputerPlayer  
from copy import deepcopy

class GameState:
    def __init__(self):
        self.current_player = COLOR_RED
        self.selected_piece_pos = None
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.red_time = 900
        self.black_time = 900
        self.last_time_update = time.time()
        self.game_started = False
        self.red_captured = []
        self.black_captured = []
        self.game_mode = None  # 'human_vs_human', 'human_vs_ai', 'ai_vs_ai'
        self.mode_selected = False  # Thêm biến này
        self.ai_thinking = False

    def update_timers(self):
        if not self.game_started or self.game_over:
            return
        
        current_time = time.time()
        elapsed = current_time - self.last_time_update
        self.last_time_update = current_time
        
        if self.current_player == COLOR_RED:
            self.red_time = max(0, self.red_time - elapsed)
            if self.red_time <= 0:
                self.game_over = True
                self.winner = COLOR_BLACK
        else:
            self.black_time = max(0, self.black_time - elapsed)
            if self.black_time <= 0:
                self.game_over = True
                self.winner = COLOR_RED

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

def get_board_pos(pixel_pos):
    """Chuyển tọa độ pixel sang vị trí trên bàn cờ"""
    x, y = pixel_pos
    if (BOARD_LEFT_MARGIN <= x < BOARD_LEFT_MARGIN + BOARD_WIDTH and
        BOARD_TOP_MARGIN <= y < BOARD_TOP_MARGIN + BOARD_HEIGHT):
        col = round((x - BOARD_LEFT_MARGIN) / SQUARE_SIZE)
        row = round((y - BOARD_TOP_MARGIN) / SQUARE_SIZE)
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
    return None

def handle_click(board, game_state, pixel_pos):
    if game_state.game_over or not game_state.game_started:
        return None

    # Nếu là chế độ AI và đến lượt AI thì không xử lý click
    if (game_state.game_mode == 'human_vs_ai' and game_state.current_player == COLOR_BLACK) or \
       (game_state.game_mode == 'ai_vs_ai'):
        return None

    board_pos = get_board_pos(pixel_pos)
    if not board_pos:
        return None

    row, col = board_pos
    clicked_piece = board.board[row][col]

    if game_state.selected_piece_pos:
        # CHỈ đổi lượt nếu nước đi hợp lệ
        move_result = board.move_piece(game_state.selected_piece_pos, board_pos)
        if move_result:  # <-- Quan trọng: chỉ xử lý nếu di chuyển thành công
            # Xử lý khi ăn quân
            if clicked_piece is not None:
                if clicked_piece.color == COLOR_RED:
                    game_state.black_captured.append(clicked_piece)
                else:
                    game_state.red_captured.append(clicked_piece)
            
            # Đổi lượt
            game_state.current_player = COLOR_BLACK if game_state.current_player == COLOR_RED else COLOR_RED
            game_state.selected_piece_pos = None
            
            # Kiểm tra chiếu bí
            if board.is_checkmate(game_state.current_player):
                game_state.game_over = True
                game_state.winner = COLOR_RED if game_state.current_player == COLOR_BLACK else COLOR_BLACK
        return None

    # Chọn quân cờ (chỉ chọn nếu đúng lượt)
    if clicked_piece and clicked_piece.color == game_state.current_player:
        return board_pos

    return None

def reset_game(game_state, board):
    """Reset trạng thái game"""
    game_state.__init__()
    board.initialize_board()

def make_ai_move(board, game_state, computer):
    if game_state.game_over or not game_state.game_started or game_state.ai_thinking:
        return
    
    # Chỉ thực hiện nếu đúng lượt của AI
    if (game_state.game_mode == 'human_vs_ai' and game_state.current_player == COLOR_BLACK) or \
       (game_state.game_mode == 'ai_vs_ai'):
        
        game_state.ai_thinking = True
        best_move = computer.get_move(deepcopy(board))
        game_state.ai_thinking = False
        
        if best_move:
            start_pos, end_pos = best_move
            # Chỉ đổi lượt nếu nước đi hợp lệ
            if board.move_piece(start_pos, end_pos):                
                # Đổi lượt
                game_state.current_player = COLOR_BLACK if game_state.current_player == COLOR_RED else COLOR_RED
                
                # Kiểm tra chiếu bí
                if board.is_checkmate(game_state.current_player):
                    game_state.game_over = True
                    game_state.winner = COLOR_RED if game_state.current_player == COLOR_BLACK else COLOR_BLACK

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cờ Tướng")
    
    # Font
    fonts = {
        'large': pygame.font.SysFont(FONT_NAME, TITLE_FONT_SIZE, bold=True),
        'medium': pygame.font.SysFont(FONT_NAME, SUBTITLE_FONT_SIZE),
        'small': pygame.font.SysFont(FONT_NAME, STATUS_FONT_SIZE)
    }

    clock = pygame.time.Clock()
    board = Board()
    board.initialize_board()
    piece_images = load_piece_images()
    game_state = GameState()
    
    # Khởi tạo AI players
    red_computer = ComputerPlayer(is_red=True, depth=3)
    black_computer = ComputerPlayer(is_red=False, depth=3)

    running = True
    while running:
        game_state.update_timers()
        
        # Xử lý AI move nếu cần
        if game_state.game_started and not game_state.game_over:
            # Thêm delay để tránh AI đi quá nhanh
            pygame.time.delay(100)  # Delay 100ms giữa các nước đi
            
            if game_state.game_mode == 'human_vs_ai' and game_state.current_player == COLOR_BLACK:
                make_ai_move(board, game_state, black_computer)
            elif game_state.game_mode == 'ai_vs_ai':
                if game_state.current_player == COLOR_RED:
                    make_ai_move(board, game_state, red_computer)
                else:
                    make_ai_move(board, game_state, black_computer)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state.game_started and not game_state.game_over:
                game_state.selected_piece_pos = handle_click(board, game_state, event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and not game_state.mode_selected:  # Changed condition
                    game_state.game_mode = 'human_vs_human'
                    game_state.mode_selected = True
                    game_state.game_started = True
                    game_state.last_time_update = time.time()
                elif event.key == pygame.K_2 and not game_state.mode_selected:  # Changed condition
                    game_state.game_mode = 'human_vs_ai'
                    game_state.mode_selected = True
                    game_state.game_started = True
                    game_state.last_time_update = time.time()
                elif event.key == pygame.K_3 and not game_state.mode_selected:  # Changed condition
                    game_state.game_mode = 'ai_vs_ai'
                    game_state.mode_selected = True
                    game_state.game_started = True
                    game_state.last_time_update = time.time()
                elif event.key == pygame.K_r:  # Reset
                    reset_game(game_state, board)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Vẽ
        if not game_state.game_started:
            draw_start_screen(screen, fonts, game_state)  # Thêm game_state vào tham số
        else:
            draw_game_interface(screen, game_state, board, piece_images, fonts)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()