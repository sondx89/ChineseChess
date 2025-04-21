from utils.const import (
    BLACK_PALACE, RED_PALACE, RIVER_ROW_TOP, RIVER_ROW_BOTTOM, BOARD_ROWS, BOARD_COLS,
    COLOR_BLACK, COLOR_RED, TYPE_GENERAL, TYPE_ADVISOR, TYPE_ELEPHANT, TYPE_HORSE, TYPE_CHARIOT, TYPE_CANNON, TYPE_SOLDIER
)

def validate_move(start_pos, end_pos, board):
    """
    Kiểm tra xem nước đi từ start_pos đến end_pos có hợp lệ hay không.
    """
    piece = board.board[start_pos[0]][start_pos[1]]
    return piece is not None and end_pos in piece.valid_positions

def is_check_condition(board, color):
    """
    Kiểm tra xem một bên có bị chiếu hay không.
    """
    general_position = board.get_general_position(color)
    opponent_color = COLOR_RED if color == COLOR_BLACK else COLOR_BLACK

    for piece in board.get_pieces_by_color(opponent_color):
        if general_position in piece.valid_positions:
            return True
    # Check xem 2 tướng có nằm trên cùng 1 cột không nếu có trả về True
    if board.get_general_position(COLOR_BLACK)[1] == board.get_general_position(COLOR_RED)[1]:
        # nếu không tồn tại quân cờ nào nằm giữa 2 tướng thì trả về True
        count_between = _count_pieces_between(
            board.get_general_position(COLOR_BLACK),
            board.get_general_position(COLOR_RED),
            board.board
        )
        if count_between == 0: 
            return True
    return False

def place_piece_on_board(board, piece, position):
    """
    Đặt một quân cờ vào một vị trí trên bàn cờ và cập nhật thông tin liên quan.
    """
    row, col = position

    # Loại bỏ quân cờ hiện tại ở vị trí đó (nếu có)
    if board.board[row][col] is not None:
        remove_piece_from_board(board, position)

    # Đặt quân cờ vào vị trí mới
    board.board[row][col] = piece
    piece.set_position(position);

    # Thêm quân cờ vào danh sách theo màu
    if piece.color == COLOR_BLACK:
        board.black_pieces.append(piece)
        if piece.type == TYPE_GENERAL:
            board.general_positions[COLOR_BLACK] = position
    else:
        board.red_pieces.append(piece)
        if piece.type == TYPE_GENERAL:
            board.general_positions[COLOR_RED] = position

    # Tính toán lại nước đi hợp lệ
    set_valid_moves(piece, board)

    # Cập nhật nước đi hợp lệ của các quân cờ khác
    for other_piece in board.get_all_pieces():
        if other_piece != piece:
            _update_valid_moves_of_pieces_when_a_position_on_board_changed(other_piece, position, board)

def remove_piece_from_board(board, position):
    """
    Loại bỏ một quân cờ khỏi một vị trí trên bàn cờ và cập nhật thông tin liên quan.
    """
    row, col = position
    piece = board.board[row][col]

    if piece:
        piece.current_position = None
        piece.can_moves = []
        piece.valid_positions = []
        board.board[row][col] = None

        # Loại bỏ quân cờ khỏi danh sách theo màu (nếu tồn tại)
        if piece.color == COLOR_BLACK and piece in board.black_pieces:
            board.black_pieces.remove(piece)
        elif piece.color == COLOR_RED and piece in board.red_pieces:
            board.red_pieces.remove(piece)

    # Cập nhật nước đi hợp lệ của các quân cờ khác
    for other_piece in board.get_all_pieces():
        _update_valid_moves_of_pieces_when_a_position_on_board_changed(other_piece, position, board)

def set_valid_moves(piece, board):
    """
    Tính toán và cập nhật các nước đi hợp lệ cho quân cờ.
    """
    piece.valid_positions = []
    move_setters = {
        TYPE_GENERAL: _set_general_moves,
        TYPE_ADVISOR: _set_advisor_moves,
        TYPE_ELEPHANT: _set_elephant_moves,
        TYPE_HORSE: _set_horse_moves,
        TYPE_CHARIOT: _set_chariot_moves,
        TYPE_CANNON: _set_cannon_moves,
        TYPE_SOLDIER: _set_soldier_moves,
    }
    move_setters.get(piece.type, lambda p, b: None)(piece, board)

def _set_general_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Tướng.
    """
    # Lấy vị trí hiện tại của Tướng
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Xác định cung mà Tướng có thể di chuyển
    palace = BLACK_PALACE if piece.color == COLOR_BLACK else RED_PALACE

    # Kiểm tra các hướng di chuyển
    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        new_row, new_col = row + dr, col + dc
        if palace["row_min"] <= new_row <= palace["row_max"] and palace["col_min"] <= new_col <= palace["col_max"]:
            # Kiểm tra xem có quân cờ nào tại vị trí mới không
            target_piece = board.board[new_row][new_col]

            if target_piece is None or target_piece.color != piece.color:
                # Kiểm tra xem nước đi này có khiến Tướng đối mặt với Tướng đối phương không
                opponent_color = COLOR_RED if piece.color == COLOR_BLACK else COLOR_BLACK
                opponent_general_position = board.get_general_position(opponent_color)

                if opponent_general_position is not None:
                    opponent_row, opponent_col = opponent_general_position

                    # Nếu Tướng đối phương nằm trên cùng cột
                    if new_col == opponent_col:
                        # Kiểm tra xem có quân cờ nào giữa hai Tướng không
                        count_between = _count_pieces_between((new_row, new_col), opponent_general_position, board.board)
                        if count_between == 0:
                            # Nếu không có quân cờ nào ở giữa, loại bỏ nước đi này
                            continue

                valid_moves.append((new_row, new_col))

    # Cập nhật danh sách nước đi hợp lệ của Tướng
    piece.valid_positions = valid_moves

def _set_advisor_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Sĩ.
    """
    # Lấy vị trí hiện tại của Sĩ
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Xác định cung mà Sĩ có thể di chuyển
    palace = BLACK_PALACE if piece.color == COLOR_BLACK else RED_PALACE

    # Kiểm tra các hướng di chuyển
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        new_row, new_col = row + dr, col + dc

        # Kiểm tra xem vị trí mới có nằm trong cung điện không
        if palace["row_min"] <= new_row <= palace["row_max"] and palace["col_min"] <= new_col <= palace["col_max"]:
            # Kiểm tra xem có quân cờ nào tại vị trí mới không
            target_piece = board.board[new_row][new_col]

            # Nếu không có quân cờ hoặc quân cờ đó không cùng màu, thêm vào danh sách nước đi hợp lệ
            if target_piece is None or target_piece.color != piece.color:
                valid_moves.append((new_row, new_col))

    # Cập nhật danh sách nước đi hợp lệ của Sĩ
    piece.valid_positions = valid_moves

def _set_elephant_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Tượng.
    """
    # Lấy vị trí hiện tại của Tượng
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Xác định khu vực mà Tượng có thể di chuyển (nửa bàn cờ của mỗi bên)
    if piece.color == COLOR_BLACK:
        min_row = 0
        max_row = RIVER_ROW_TOP  # Tượng đen không được vượt qua sông
    else:
        min_row = RIVER_ROW_BOTTOM  # Tượng đỏ không được vượt qua sông
        max_row = BOARD_ROWS


    # Kiểm tra các hướng di chuyển
    for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        new_row, new_col = row + dr, col + dc
        # Kiểm tra xem vị trí mới có nằm trên bàn cờ và trong khu vực của Tượng không
        if min_row <= new_row <= max_row and 0 <= new_col < BOARD_COLS:
            # Kiểm tra xem có quân cờ nào tại vị trí mới không
            target_piece = board.board[new_row][new_col]

            # Kiểm tra xem có bị chặn ở "mắt" không
            block_row, block_col = row + dr // 2, col + dc // 2
            if board.board[block_row][block_col] is None:
                # Nếu không có quân cờ hoặc quân cờ đó không cùng màu, thêm vào danh sách nước đi hợp lệ
                if target_piece is None or target_piece.color != piece.color:
                    valid_moves.append((new_row, new_col))

    # Cập nhật danh sách nước đi hợp lệ của Tượng
    piece.valid_positions = valid_moves

def _set_horse_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Mã.
    """
    # Lấy vị trí hiện tại của Mã
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Các hướng di chuyển của Mã (hình chữ L)
    move_directions = [
        (-2, -1, -1, 0), (-2, 1, -1, 0), (2, -1, 1, 0), (2, 1, 1, 0),
        (-1, -2, 0, -1), (-1, 2, 0, 1), (1, -2, 0, -1), (1, 2, 0, 1)
    ]

    # Kiểm tra từng hướng di chuyển
    for dr, dc, block_dr, block_dc in move_directions:
        new_row, new_col = row + dr, col + dc
        # Kiểm tra xem vị trí mới có nằm trên bàn cờ không
        if 0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS:
            # Kiểm tra xem có bị chặn ở "chân" không
            block_row, block_col = row + block_dr, col + block_dc
            if board.board[block_row][block_col] is None:
                # Nếu không bị chặn, kiểm tra xem có quân cờ nào tại vị trí mới không
                target_piece = board.board[new_row][new_col]

                # Nếu không có quân cờ hoặc quân cờ đó không cùng màu, thêm vào danh sách nước đi hợp lệ
                if target_piece is None or target_piece.color != piece.color:
                    valid_moves.append((new_row, new_col))

    # Cập nhật danh sách nước đi hợp lệ của Mã
    piece.valid_positions = valid_moves

def _set_chariot_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Xe.
    """
    # Lấy vị trí hiện tại của Xe
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Kiểm tra theo chiều ngang và chiều dọc
    for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        row_dir, col_dir = direction

        # Tìm các vị trí có thể di chuyển đến
        for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
            new_row, new_col = row + i * row_dir, col + i * col_dir

            # Kiểm tra xem vị trí mới có nằm trên bàn cờ không
            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                break  # Ra khỏi bàn cờ

            # Kiểm tra xem có quân cờ nào trên đường đi không
            target_piece = board.board[new_row][new_col]

            if target_piece is None:
                # Nếu không có quân cờ, thêm vào danh sách nước đi hợp lệ
                valid_moves.append((new_row, new_col))
            else:
                # Nếu có quân cờ, kiểm tra xem có phải quân đối phương không
                if target_piece.color != piece.color:
                    # Nếu là quân đối phương, thêm vào danh sách nước đi hợp lệ
                    valid_moves.append((new_row, new_col))
                break  # Dừng lại sau khi tìm thấy quân cờ

    # Cập nhật danh sách nước đi hợp lệ của Xe
    piece.valid_positions = valid_moves

def _set_cannon_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Pháo.
    """
    # Lấy vị trí hiện tại của Pháo
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Kiểm tra theo chiều ngang và chiều dọc
    for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        row_dir, col_dir = direction
        
        # Tìm các vị trí có thể di chuyển đến
        found_obstacle = False  # Biến để theo dõi xem đã gặp chướng ngại vật chưa
        for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
            new_row, new_col = row + i * row_dir, col + i * col_dir

            # Kiểm tra xem vị trí mới có nằm trên bàn cờ không
            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                break  # Ra khỏi bàn cờ

            # Kiểm tra xem có quân cờ nào trên đường đi không
            target_piece = board.board[new_row][new_col]

            if not found_obstacle:
                if target_piece is None:
                    # Nếu không có quân cờ và chưa gặp chướng ngại vật, thêm vào danh sách nước đi hợp lệ
                    valid_moves.append((new_row, new_col))
                else:
                    # Nếu có quân cờ và chưa gặp chướng ngại vật, đánh dấu là đã gặp chướng ngại vật
                    found_obstacle = True
            else:
                if target_piece is not None:
                    # Nếu đã gặp chướng ngại vật và có quân cờ tại vị trí này
                    if target_piece.color != piece.color:
                        # Nếu là quân đối phương, thêm vào danh sách nước đi hợp lệ (ăn quân)
                        valid_moves.append((new_row, new_col))
                    break  # Dừng lại sau khi ăn quân
    # Cập nhật danh sách nước đi hợp lệ của Pháo
    piece.valid_positions = valid_moves

def _set_soldier_moves(piece, board):
    """
    Tính toán các nước đi hợp lệ cho quân Tốt.
    """
    # Lấy vị trí hiện tại của Tốt
    row, col = piece.current_position

    # Tạo danh sách các nước đi hợp lệ
    valid_moves = []

    # Xác định hướng di chuyển của Tốt dựa trên màu sắc
    if piece.color == COLOR_BLACK:
        forward_direction = 1  # Tốt đen đi xuống
        can_move_sideways = row > RIVER_ROW_TOP  # Tốt đen chỉ được đi ngang sau khi qua sông
    else:
        forward_direction = -1  # Tốt đỏ đi lên
        can_move_sideways = row < RIVER_ROW_BOTTOM  # Tốt đỏ chỉ được đi ngang sau khi qua sông

    # Kiểm tra hướng đi thẳng
    new_row = row + forward_direction
    if 0 <= new_row < BOARD_ROWS:
        target_piece = board.board[new_row][col]
        if target_piece is None or target_piece.color != piece.color:
            valid_moves.append((new_row, col))

    # Kiểm tra hướng đi ngang nếu đã qua sông
    if can_move_sideways:
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_col < BOARD_COLS:
                target_piece = board.board[row][new_col]
                if target_piece is None or target_piece.color != piece.color:
                    valid_moves.append((row, new_col))

    # Cập nhật danh sách nước đi hợp lệ của Tốt
    piece.valid_positions = valid_moves

def _count_pieces_between(start_pos, end_pos, board):
    """
    Đếm số quân cờ nằm giữa hai vị trí trên bàn cờ.
    :param start_pos: Tuple (row, col) - vị trí bắt đầu.
    :param end_pos: Tuple (row, col) - vị trí kết thúc.
    :param board: Bàn cờ hiện tại (danh sách 2D).
    :return: Số lượng quân cờ nằm giữa hai vị trí.
    """
    count = -1
    row_start, col_start = start_pos
    row_end, col_end = end_pos

    # Nếu hai vị trí nằm trên cùng hàng hoặc cột
    if row_start == row_end:
        count = 0
        for col in range(min(col_start, col_end) + 1, max(col_start, col_end)):
            if board[row_start][col] is not None:
                count += 1
    elif col_start == col_end:
        count = 0
        for row in range(min(row_start, row_end) + 1, max(row_start, row_end)):
            if board[row][col_start] is not None:
                count += 1

    return count

def _update_valid_moves_of_pieces_when_a_position_on_board_changed(piece, position, board):
    """
    Cập nhật các nước đi hợp lệ của quân cờ khi một vị trí trên bàn cờ thay đổi.
    :param piece: Đối tượng quân cờ (Piece).
    :param position: Tuple (row, col) - vị trí đã thay đổi.
    :param board: Bàn cờ hiện tại (danh sách 2D).
    """
    # Lấy các nước đi có thể hiện tại của quân cờ
    can_moves = piece.can_moves.copy()
    # Lấy các nước đi hợp lệ hiện tại của quân cờ
    valid_moves = piece.valid_positions.copy()
    # Nếu vị trí thay đổi nằm trong các nước đi hợp lệ, tính toán lại nước đi hợp lệ
    if position in can_moves:
        target_piece = board.board[position[0]][position[1]]
        # Nếu có quân cờ tại vị trí này, loại bỏ vị trí này khỏi các nước đi hợp lệ
        if piece.type in [TYPE_GENERAL, TYPE_ADVISOR, TYPE_ELEPHANT, TYPE_HORSE, TYPE_SOLDIER]:
            if target_piece is None and position not in valid_moves:
                valid_moves.append(position)
            elif target_piece is not None and target_piece.color == piece.color and position in valid_moves:
                valid_moves.remove(position)
            piece.valid_positions = valid_moves
        else:
            set_valid_moves (piece, board) 
    elif piece.type in [TYPE_HORSE, TYPE_ELEPHANT, TYPE_CANNON]:
        _special_update_moves(piece, position, board)

def _special_update_moves(piece, position, board):
    """
    Xử lý cập nhật nước đi cho các quân cờ có logic đặc biệt.
    """
    if piece.type == TYPE_HORSE:
        _update_horse_moves(piece, position, board)
    elif piece.type == TYPE_ELEPHANT:
        _update_elephant_moves(piece, position, board)
    elif piece.type == TYPE_CANNON:
        if piece.current_position[0] == position[0] or piece.current_position[1] == position[1]:
            set_valid_moves(piece, board)

def _update_horse_moves(piece, position, board):
    """
    Cập nhật nước đi hợp lệ của quân Mã khi một vị trí trên bàn cờ thay đổi.
    """
    row, col = piece.current_position
    valid_moves = piece.valid_positions.copy()
    target_piece = board.board[position[0]][position[1]]
    # Các vị trí chặn nước đi của Mã
    block_positions = [
        (row, col - 1), (row, col + 1),  # Chặn ngang
        (row - 1, col), (row + 1, col)   # Chặn dọc
    ]

    for block_row, block_col in block_positions:
        if position == (block_row, block_col):
            # Nếu vị trí thay đổi là vị trí chặn, loại bỏ các nước đi bị ảnh hưởng
            if block_row == row:
                # Chặn ngang
                invalid_moves = [
                    (row - 1, col + (block_col - col) * 2),
                    (row + 1, col + (block_col - col) * 2)
                ]
            else:
                # Chặn dọc
                invalid_moves = [
                    (row + (block_row - row) * 2, col - 1),
                    (row + (block_row - row) * 2, col + 1)
                ]
            for move in invalid_moves:
                if target_piece is None:
                    if move not in valid_moves:
                        if 0<= move[0] < BOARD_ROWS and 0<= move[1] < BOARD_COLS:
                            valid_moves.append(move)
                else:
                    if move in valid_moves:
                        valid_moves.remove(move)

    piece.valid_positions = valid_moves

def _update_elephant_moves(piece, position, board):
    """
    Cập nhật nước đi hợp lệ của quân Tượng khi một vị trí trên bàn cờ thay đổi.
    """
    row, col = piece.current_position
    valid_moves = piece.valid_positions.copy()
    target_piece = board.board[position[0]][position[1]]
    # Các vị trí chặn nước đi của Tượng
    block_positions = [
        (row + dr // 2, col + dc // 2)
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]
    ]

    for block_row, block_col in block_positions:
        if position == (block_row, block_col):
            # Nếu vị trí thay đổi là vị trí chặn, loại bỏ nước đi bị ảnh hưởng
            invalid_move = (row + (block_row - row) * 2, col + (block_col - col) * 2)
            if target_piece is None:
                if invalid_move not in valid_moves:
                    valid_moves.append(invalid_move)
            else:
                if invalid_move in valid_moves:
                    valid_moves.remove(invalid_move)

    piece.valid_positions = valid_moves

