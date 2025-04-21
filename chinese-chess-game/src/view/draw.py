import pygame
import os
from utils.const import *
from game.pieces import *

def load_piece_images():
    """Load và resize ảnh quân cờ"""
    pieces = [
        General(COLOR_BLACK), Advisor(COLOR_BLACK), Elephant(COLOR_BLACK), 
        Horse(COLOR_BLACK), Chariot(COLOR_BLACK), Cannon(COLOR_BLACK), 
        Soldier(COLOR_BLACK),
        General(COLOR_RED), Advisor(COLOR_RED), Elephant(COLOR_RED), 
        Horse(COLOR_RED), Chariot(COLOR_RED), Cannon(COLOR_RED), 
        Soldier(COLOR_RED)
    ]

    piece_images = {}
    target_size = int(SQUARE_SIZE * PIECE_SCALE)
    
    for piece in pieces:
        try:
            img = pygame.image.load(os.path.join(os.path.dirname(__file__), "..", piece.image_path))
            img = pygame.transform.smoothscale(img, (target_size, target_size))
            piece_images[piece.name] = img
        except:
            # Fallback nếu không load được ảnh
            surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
            color = COLOR_RED if piece.color == COLOR_RED else COLOR_BLACK
            pygame.draw.circle(surf, color, (target_size//2, target_size//2), target_size//2)
            piece_images[piece.name] = surf
    
    return piece_images

def draw_board(screen):
    """Vẽ bàn cờ với các đường kẻ và thành phần"""
    # Vẽ nền bàn cờ
    board_rect = pygame.Rect(
        BOARD_LEFT_MARGIN - 10, 
        BOARD_TOP_MARGIN - 10, 
        BOARD_WIDTH + 20, 
        BOARD_HEIGHT + 20
    )
    pygame.draw.rect(screen, BOARD_COLOR, board_rect, border_radius=5)
    
    # Vẽ đường kẻ ngang
    for r in range(BOARD_ROWS):
        y = BOARD_TOP_MARGIN + r * SQUARE_SIZE
        pygame.draw.line(
            screen, LINE_COLOR, 
            (BOARD_LEFT_MARGIN, y), 
            (BOARD_LEFT_MARGIN + BOARD_WIDTH, y), 
            2
        )
    
    # Vẽ đường kẻ dọc
    for c in range(BOARD_COLS):
        x = BOARD_LEFT_MARGIN + c * SQUARE_SIZE
        pygame.draw.line(
            screen, LINE_COLOR, 
            (x, BOARD_TOP_MARGIN), 
            (x, BOARD_TOP_MARGIN + BOARD_HEIGHT), 
            2
        )
    
    # Vẽ sông (chỉ 1 ô giữa hàng 4 và 5)
    river_y = BOARD_TOP_MARGIN + RIVER_ROW_TOP * SQUARE_SIZE
    river_rect = pygame.Rect(
        BOARD_LEFT_MARGIN, river_y, 
        BOARD_WIDTH, SQUARE_SIZE  # Chỉ cao 1 SQUARE_SIZE
    )
    s = pygame.Surface((river_rect.width, river_rect.height), pygame.SRCALPHA)
    s.fill(RIVER_COLOR)
    screen.blit(s, river_rect)
    
    # Vẽ chữ "SÔNG" ở giữa sông
    font = pygame.font.SysFont(FONT_NAME, 24, bold=True)
    text = font.render("SÔNG", True, LINE_COLOR)
    text_rect = text.get_rect(center=(
        BOARD_LEFT_MARGIN + BOARD_WIDTH//2, 
        river_y + SQUARE_SIZE//2
    ))
    screen.blit(text, text_rect)
    
    # Vẽ cung
    _draw_palace(screen, BLACK_PALACE)
    _draw_palace(screen, RED_PALACE)

def _draw_palace(screen, palace):
    """Vẽ đường chéo trong cung"""
    x1 = BOARD_LEFT_MARGIN + palace["col_min"] * SQUARE_SIZE
    y1 = BOARD_TOP_MARGIN + palace["row_min"] * SQUARE_SIZE
    x2 = BOARD_LEFT_MARGIN + palace["col_max"] * SQUARE_SIZE
    y2 = BOARD_TOP_MARGIN + palace["row_max"] * SQUARE_SIZE
    
    pygame.draw.line(screen, LINE_COLOR, (x1, y1), (x2, y2), 2)
    pygame.draw.line(screen, LINE_COLOR, (x2, y1), (x1, y2), 2)

def draw_pieces(screen, board, piece_images):
    """Vẽ các quân cờ lên bàn cờ"""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            piece = board[row][col]
            if piece:
                img = piece_images[piece.name]
                x = BOARD_LEFT_MARGIN + col * SQUARE_SIZE
                y = BOARD_TOP_MARGIN + row * SQUARE_SIZE
                img_rect = img.get_rect(center=(x, y))
                screen.blit(img, img_rect)

def draw_highlight(screen, pos):
    """Vẽ highlight cho quân cờ được chọn"""
    if pos:
        row, col = pos
        x = BOARD_LEFT_MARGIN + col * SQUARE_SIZE
        y = BOARD_TOP_MARGIN + row * SQUARE_SIZE
        
        s = pygame.Surface(
            (HIGHLIGHT_CIRCLE_RADIUS*2, HIGHLIGHT_CIRCLE_RADIUS*2), 
            pygame.SRCALPHA
        )
        pygame.draw.circle(
            s, HIGHLIGHT_COLOR, 
            (HIGHLIGHT_CIRCLE_RADIUS, HIGHLIGHT_CIRCLE_RADIUS), 
            HIGHLIGHT_CIRCLE_RADIUS, 3
        )
        screen.blit(s, (x-HIGHLIGHT_CIRCLE_RADIUS, y-HIGHLIGHT_CIRCLE_RADIUS))

def draw_captured_pieces(screen, captured_pieces, piece_images, start_pos, title, font):
    """Vẽ các quân cờ đã bị ăn"""
    x, y = start_pos
    title_surf = font.render(title, True, TEXT_COLOR)
    screen.blit(title_surf, (x, y))
    y += 40
    
    for i, piece in enumerate(captured_pieces):
        if i % 6 == 0 and i != 0:  # 6 quân mỗi hàng
            y += 50
            x = start_pos[0]
        
        img = piece_images[piece.name]
        screen.blit(img, (x, y))
        x += 50

def draw_start_screen(screen, fonts, game_state):
    """Vẽ màn hình bắt đầu với các lựa chọn chế độ chơi"""
    screen.fill(BACKGROUND_COLOR)
    
    # Tiêu đề
    title = fonts['large'].render("CỜ TƯỚNG", True, TEXT_GOLD)
    title_shadow = fonts['large'].render("CỜ TƯỚNG", True, (100, 100, 100))
    
    # Các lựa chọn chế độ chơi
    option1 = fonts['medium'].render("1. Hai người chơi", True, TEXT_COLOR)
    option2 = fonts['medium'].render("2. Người chơi vs Máy", True, TEXT_COLOR)
    option3 = fonts['medium'].render("3. Máy vs Máy", True, TEXT_COLOR)
    
    # Vẽ với hiệu ứng bóng đổ cho tiêu đề
    screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, SCREEN_HEIGHT//4 + 3))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
    
    # Vẽ các lựa chọn chế độ chơi
    screen.blit(option1, (SCREEN_WIDTH//2 - option1.get_width()//2, SCREEN_HEIGHT//2 - 30))
    screen.blit(option2, (SCREEN_WIDTH//2 - option2.get_width()//2, SCREEN_HEIGHT//2 + 20))
    screen.blit(option3, (SCREEN_WIDTH//2 - option3.get_width()//2, SCREEN_HEIGHT//2 + 70))
    
    # Hiển thị thông báo khi chọn mode
    if game_state.mode_selected:
        mode_text = ""
        if game_state.game_mode == 'human_vs_human':
            mode_text = "Đã chọn: Hai người chơi"
        elif game_state.game_mode == 'human_vs_ai':
            mode_text = "Đã chọn: Người chơi vs Máy"
        elif game_state.game_mode == 'ai_vs_ai':
            mode_text = "Đã chọn: Máy vs Máy"
        
        selected_text = fonts['small'].render(mode_text, True, TEXT_GOLD)
        screen.blit(selected_text, (SCREEN_WIDTH//2 - selected_text.get_width()//2, SCREEN_HEIGHT - 120))
    
    # Hướng dẫn
    instruction = fonts['small'].render("Chọn chế độ chơi bằng phím 1, 2 hoặc 3", True, TEXT_COLOR)
    controls = fonts['small'].render("Nhấn SPACE để bắt đầu | ESC: Thoát", True, TEXT_COLOR)
    screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT - 80))
    screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, SCREEN_HEIGHT - 40))

def draw_game_interface(screen, game_state, board, piece_images, fonts):
    """Vẽ toàn bộ giao diện game"""
    # Nền
    screen.fill(BACKGROUND_COLOR)
    
    # Bàn cờ
    draw_board(screen)
    draw_pieces(screen, board.board, piece_images)
    
    # Highlight quân được chọn
    if game_state.selected_piece_pos:
        selected_piece = board.board[game_state.selected_piece_pos[0]][game_state.selected_piece_pos[1]]
        draw_highlight(screen, game_state.selected_piece_pos)
        if selected_piece and selected_piece.color == game_state.current_player:
            for pos in selected_piece.valid_positions:
                draw_highlight(screen, pos)
    
    # Đồng hồ
    black_time = fonts['medium'].render(
        f"ĐEN: {game_state.format_time(game_state.black_time)}", 
        True, pygame.Color('black')
    )
    red_time = fonts['medium'].render(
        f"ĐỎ: {game_state.format_time(game_state.red_time)}", 
        True, pygame.Color('red')
    )
    screen.blit(black_time, (50, 30))
    screen.blit(red_time, (50, SCREEN_HEIGHT - 60))
    
    # Quân bị ăn
    draw_captured_pieces(
        screen, game_state.black_captured, piece_images, 
        (SCREEN_WIDTH - 200, 30), "Quân Đỏ bị ăn", fonts['small']
    )
    draw_captured_pieces(
        screen, game_state.red_captured, piece_images,
        (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150), 
        "Quân Đen bị ăn", fonts['small']
    )
    
    # Thanh trạng thái
    status_bar = pygame.Rect(0, SCREEN_HEIGHT - STATUS_BAR_HEIGHT, SCREEN_WIDTH, STATUS_BAR_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), status_bar)
    
    status_text = ""
    if game_state.game_over:
        status_text = f"{'ĐỎ' if game_state.winner == COLOR_RED else 'ĐEN'} THẮNG! Nhấn R để chơi lại"
    else:
        status_text = f"Lượt đi: {'ĐỎ' if game_state.current_player == COLOR_RED else 'ĐEN'} | R: Reset | U: Undo"
    
    text = fonts['small'].render(status_text, True, TEXT_WHITE)
    screen.blit(text, (20, SCREEN_HEIGHT - STATUS_BAR_HEIGHT + 10))
