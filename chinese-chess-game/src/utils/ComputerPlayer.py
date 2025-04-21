import random
from collections import defaultdict
from copy import deepcopy
from utils.const import *

class ComputerPlayer:
    def __init__(self, is_red, depth=3):
        self.is_red = is_red
        self.depth = depth
        self.transposition_table = {}
        self.killer_moves = defaultdict(list)
        self.history_table = defaultdict(int)
        self._pos_score_cache = {}  # Cache cho điểm vị trí
        
        self.piece_values = {
            TYPE_GENERAL: 10000,
            TYPE_CHARIOT: 900,
            TYPE_CANNON: 450,
            TYPE_HORSE: 300,
            TYPE_ELEPHANT: 150,
            TYPE_ADVISOR: 120,
            TYPE_SOLDIER: {
                'before_river': 60,
                'after_river': 100,
                'near_palace': 80
            }
        }
        
        self.eval_weights = {
            'material': 1.2,
            'position': 0.8,
            'center_control': 1.5,
            'threats': 1.0,
            'mobility': 0.6,
            'king_safety': 2.0,
            'piece_coordination': 0.4,
            'pawn_structure': 0.5
        }
        
        self.position_scores = self._init_position_scores()
        self.simulator_board = None
        self.eval_cache = {}
        self.move_gen_cache = {}

    # Replace the _init_position_scores method with:
    def _init_position_scores(self):
        """Khởi tạo bảng điểm vị trí không dùng numpy"""
        base_scores = [
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0, 10, 20, 10,  0,  0,  0],
            [0,  0, 10, 20, 30, 20, 10,  0,  0],
            [0, 10, 20, 30, 40, 30, 20, 10,  0],
            [0, 20, 30, 40, 50, 40, 30, 20,  0],
            [0, 10, 20, 30, 40, 30, 20, 10,  0],
            [0,  0, 10, 20, 30, 20, 10,  0,  0],
            [0,  0,  0, 10, 20, 10,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        scores = {
            TYPE_CHARIOT: base_scores,
            TYPE_CANNON: [[int(score * 0.8) for score in row] for row in base_scores],
            TYPE_HORSE: [[int(score * 0.7) for score in row] for row in base_scores],
            TYPE_ELEPHANT: [[int(score * 0.5) for score in row] for row in base_scores],
            TYPE_ADVISOR: [[int(score * 0.3) for score in row] for row in base_scores],
            TYPE_SOLDIER: [[int(score * 0.6) for score in row] for row in base_scores],
            TYPE_GENERAL: [[0]*9 for _ in range(10)]
        }
        
        # Điều chỉnh điểm cho tướng trong cung
        for r in range(7, 10):
            for c in range(3, 6):
                scores[TYPE_GENERAL][r][c] = 20  # Cung đen
        for r in range(0, 3):
            for c in range(3, 6):
                scores[TYPE_GENERAL][r][c] = 20  # Cung đỏ
                
        return scores

    def get_move(self, board):
        """Tìm nước đi tốt nhất với cải tiến hiệu suất"""
        self.simulator_board = deepcopy(board)
        self.eval_cache.clear()  # Xóa cache cũ
        
        # Lấy nước đi hợp lệ với cache
        cache_key = hash(str(board.board))
        if cache_key in self.move_gen_cache:
            all_valid_moves = self.move_gen_cache[cache_key]
        else:
            all_valid_moves = self._get_all_valid_moves()
            self.move_gen_cache[cache_key] = all_valid_moves
            
        if not all_valid_moves:
            return None
            
        # Tìm nước đi tốt nhất
        best_move = None
        best_score = -float('inf') if self.is_red else float('inf')
        
        # Sắp xếp nước đi theo heuristic
        sorted_moves = self._sort_moves(all_valid_moves)
        
        # Giới hạn số nước đi xem xét ở độ sâu cao
        max_moves_to_consider = 15 if self.depth >= 3 else float('inf')
        
        for i, move in enumerate(sorted_moves):
            if i >= max_moves_to_consider:
                break
                
            start_pos, end_pos = move
            self.simulator_board.simulator_move(start_pos, end_pos)
            
            # Sử dụng Principal Variation Search để tối ưu
            if i == 0:
                score = -self.nega_scout(self.depth - 1, -float('inf'), float('inf'), not self.is_red)
            else:
                score = -self.nega_scout(self.depth - 1, -float('inf'), -best_score, not self.is_red)
                if best_score < score < float('inf'):
                    score = -self.nega_scout(self.depth - 1, -float('inf'), -score, not self.is_red)
            
            self.simulator_board.undo_simulator_move(start_pos, end_pos)
            
            if (self.is_red and score > best_score) or (not self.is_red and score < best_score):
                best_score = score
                best_move = move
                
                # Cập nhật killer moves và history heuristic
                self._update_heuristics(move)
        
        return best_move if best_move else random.choice(all_valid_moves)
    
    def _update_heuristics(self, move):
        """Cập nhật các heuristic sau khi tìm thấy nước đi tốt"""
        depth = self.depth
        if move not in self.killer_moves[depth]:
            self.killer_moves[depth].insert(0, move)
            if len(self.killer_moves[depth]) > 2:
                self.killer_moves[depth].pop()
        
        self.history_table[move] += depth * depth

    def _get_all_valid_moves(self):
        """Lấy tất cả nước đi hợp lệ cho bên hiện tại"""
        valid_moves = []
        pieces = self.simulator_board.red_pieces if self.is_red else self.simulator_board.black_pieces
        
        for piece in pieces:
            if not piece.current_position:
                continue
                
            for end_pos in piece.valid_positions:
                # Kiểm tra nước đi hợp lệ trên bàn cờ ảo
                if self._is_valid_move(piece.current_position, end_pos):
                    valid_moves.append((piece.current_position, end_pos))
        
        return valid_moves

    def _is_valid_move(self, start_pos, end_pos):
        """Kiểm tra nước đi có hợp lệ trên bàn cờ ảo không"""
        # Tạo bản sao tạm để kiểm tra
        temp_board = deepcopy(self.simulator_board)
        return temp_board.move_piece(start_pos, end_pos)

    def nega_scout(self, depth, alpha, beta, is_maximizing):
        # Kiểm tra kết thúc game trước
        if self.simulator_board.is_checkmate(COLOR_RED if is_maximizing else COLOR_BLACK):
            return -float('inf') if is_maximizing else float('inf')
        
        if self.simulator_board.is_stalemate(COLOR_RED if is_maximizing else COLOR_BLACK):
            return 0
        """Thuật toán NegaScout cải tiến"""
        # Kiểm tra bảng transposition
        board_hash = hash(str(self.simulator_board.board))
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']
        
        # Kiểm tra kết thúc game hoặc độ sâu
        if depth == 0 or self.simulator_board.is_checkmate(COLOR_RED if is_maximizing else COLOR_BLACK):
            score = self.quiescence_search(self.simulator_board, alpha, beta, is_maximizing)
            self.transposition_table[board_hash] = {'depth': depth, 'score': score}
            return score
        
        # Lấy và sắp xếp các nước đi
        moves = self._get_all_valid_moves()
        if not moves:
            return self.evaluate_board(self.simulator_board, is_maximizing) 
        
        # Sắp xếp theo heuristic
        sorted_moves = self._sort_moves(moves)
        
        best_score = -float('inf')
        for i, move in enumerate(sorted_moves):
            start_pos, end_pos = move
            
            # Thực hiện nước đi ảo
            self.simulator_board.simulator_move(start_pos, end_pos)
            
            # Tính điểm
            if i == 0:
                score = -self.nega_scout(depth - 1, -beta, -alpha, not is_maximizing)
            else:
                score = -self.nega_scout(depth - 1, -alpha - 1, -alpha, not is_maximizing)
                if alpha < score < beta:
                    score = -self.nega_scout(depth - 1, -beta, -score, not is_maximizing)
            
            # Hoàn tác
            self.simulator_board.undo_simulator_move(start_pos, end_pos)
            
            # Cập nhật alpha/beta
            if score > best_score:
                best_score = score
                if score > alpha:
                    alpha = score
                    self.history_table[(start_pos, end_pos)] += depth * depth
                    
            if alpha >= beta:
                # Lưu killer move
                if move not in self.killer_moves[depth]:
                    self.killer_moves[depth].insert(0, move)
                    if len(self.killer_moves[depth]) > 2:
                        self.killer_moves[depth].pop()
                break
        
        self.transposition_table[board_hash] = {'depth': depth, 'score': best_score}
        return best_score

    def _sort_moves(self, moves):
        """Sắp xếp các nước đi theo heuristic"""
        scored_moves = []
        for move in moves:
            score = 0
            start_pos, end_pos = move
            
            # Ưu tiên ăn quân
            target = self.simulator_board.get_piece_at(*end_pos)
            if target:
                score += self._get_piece_value(target) * 10  # Use helper method
            
            # Ưu tiên killer moves và history moves
            if move in self.killer_moves.get(self.depth, []):
                score += 500
            score += self.history_table.get(move, 0)
            
            # Ưu tiên vị trí tốt
            piece = self.simulator_board.get_piece_at(*start_pos)
            if piece:
                score += self._get_position_score(piece.type, end_pos[0], end_pos[1])
            
            scored_moves.append((score, move))
        
        # Sắp xếp giảm dần
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    def _get_piece_value(self, piece):
        """Lấy giá trị quân cờ một cách an toàn, xử lý riêng cho tốt"""
        if piece.type == TYPE_SOLDIER:
            r, c = piece.current_position
            if (piece.color == COLOR_RED and r <= RIVER_ROW_TOP) or \
            (piece.color == COLOR_BLACK and r >= RIVER_ROW_BOTTOM):
                return self.piece_values[TYPE_SOLDIER]['after_river']
            elif (3 <= c <= 5) and ((piece.color == COLOR_RED and r >= 7) or \
                                (piece.color == COLOR_BLACK and r <= 2)):
                return self.piece_values[TYPE_SOLDIER]['near_palace']
            else:
                return self.piece_values[TYPE_SOLDIER]['before_river']
        return self.piece_values.get(piece.type, 0)

    def evaluate_board(self, board, is_maximizing):
        """Đánh giá bàn cờ với nhiều yếu tố cải tiến"""
        # Kiểm tra cache trước
        cache_key = hash(str(board.board))
        if cache_key in self.eval_cache:
            return self.eval_cache[cache_key] if is_maximizing else -self.eval_cache[cache_key]

        # 1. Kiểm tra kết thúc game trước (ưu tiên cao)
        if board.is_checkmate(COLOR_RED):
            return float('inf') if is_maximizing else -float('inf')
        if board.is_checkmate(COLOR_BLACK):
            return -float('inf') if is_maximizing else float('inf')
        if board.is_stalemate(COLOR_RED) or board.is_stalemate(COLOR_BLACK):
            return 0

        # Khởi tạo các thành phần đánh giá
        evaluation = 0
        
        # 2. Điểm vật chất (Material)
        red_material, black_material = 0, 0
        piece_counts = {COLOR_RED: defaultdict(int), COLOR_BLACK: defaultdict(int)}
        
        for piece in board.get_all_pieces():
            if not piece or not piece.current_position:
                continue
                
            value = self._get_piece_value(piece)
            if piece.color == COLOR_RED:
                red_material += value
            else:
                black_material += value
            piece_counts[piece.color][piece.type] += 1

        material_diff = red_material - black_material
        
        # 3. Điểm vị trí (Positional)
        positional_score = self._evaluate_position(board)
        
        # 4. Kiểm soát trung tâm (Center Control)
        center_control = self._evaluate_center_control(board)
        
        # 5. Các mối đe dọa (Threats)
        threats = self._evaluate_threats(board)
        
        # 6. Khả năng di chuyển (Mobility)
        mobility = self._evaluate_mobility(board)
        
        # 7. An toàn tướng (King Safety)
        king_safety = self._evaluate_king_safety(board)
        
        # 8. Phối hợp quân (Piece Coordination)
        piece_coord = self._evaluate_piece_coordination(board)
        
        # 9. Cấu trúc tốt (Pawn Structure)
        pawn_structure = self._evaluate_pawn_structure(board)
        
        # 10. Điểm đặc biệt (Special Bonuses)
        special_bonuses = self._evaluate_special_features(board, piece_counts)
        
        # Tính tổng điểm có trọng số
        evaluation = (
            material_diff * self.eval_weights['material'] +
            positional_score * self.eval_weights['position'] +
            center_control * self.eval_weights['center_control'] +
            threats * self.eval_weights['threats'] +
            mobility * self.eval_weights['mobility'] +
            king_safety * self.eval_weights['king_safety'] +
            piece_coord * self.eval_weights['piece_coordination'] +
            pawn_structure * self.eval_weights['pawn_structure'] +
            special_bonuses
        )
        
        # Lưu vào cache (lưu giá trị từ góc độ RED)
        self.eval_cache[cache_key] = evaluation
        
        # Trả về giá trị phù hợp với người chơi hiện tại
        return evaluation if is_maximizing else -evaluation

    def _evaluate_special_features(self, board, piece_counts):
        """Tính điểm cho các đặc điểm đặc biệt"""
        bonuses = 0
        
        # 1. Ưu thế xe đôi (Double Rook)
        if piece_counts[COLOR_RED][TYPE_CHARIOT] >= 2:
            bonuses += 50
        if piece_counts[COLOR_BLACK][TYPE_CHARIOT] >= 2:
            bonuses -= 50
            
        # 2. Pháo đầu (Cannon in front of pawn)
        for piece in board.get_pieces_by_color(COLOR_RED):
            if piece.type == TYPE_CANNON:
                r, c = piece.current_position
                if any(p.type == TYPE_SOLDIER and p.current_position[1] == c 
                    for p in board.get_pieces_by_color(COLOR_RED)):
                    bonuses += 30
                    
        for piece in board.get_pieces_by_color(COLOR_BLACK):
            if piece.type == TYPE_CANNON:
                r, c = piece.current_position
                if any(p.type == TYPE_SOLDIER and p.current_position[1] == c 
                    for p in board.get_pieces_by_color(COLOR_BLACK)):
                    bonuses -= 30
                    
        # 3. Tốt qua sông liên thông (Connected passed pawns)
        red_pawns = [p for p in board.get_pieces_by_color(COLOR_RED) 
                    if p.type == TYPE_SOLDIER and p.current_position[0] <= RIVER_ROW_TOP]
        black_pawns = [p for p in board.get_pieces_by_color(COLOR_BLACK) 
                    if p.type == TYPE_SOLDIER and p.current_position[0] >= RIVER_ROW_BOTTOM]
        
        if len(red_pawns) >= 2 and self._are_pawns_connected(red_pawns):
            bonuses += 40
        if len(black_pawns) >= 2 and self._are_pawns_connected(black_pawns):
            bonuses -= 40
            
        return bonuses

    def _are_pawns_connected(self, pawns):
        """Kiểm tra các tốt có liên thông không"""
        for i in range(len(pawns)):
            for j in range(i+1, len(pawns)):
                r1, c1 = pawns[i].current_position
                r2, c2 = pawns[j].current_position
                if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
                    return True
        return False

    def _evaluate_center_control(self, board):
        """Đánh giá kiểm soát trung tâm"""
        control = 0
        center_squares = [(r, c) for r in range(3, 7) for c in range(3, 6)]
        
        for r, c in center_squares:
            piece = board.get_piece_at(r, c)
            if piece:
                control += 1 if piece.color == COLOR_RED else -1
        
        return control

    def _evaluate_threats(self, board):
        """Đánh giá các mối đe dọa trên bàn cờ"""
        threat_score = 0
        
        for piece in board.get_all_pieces():
            if not piece or piece.current_position is None:
                continue
                
            is_red = piece.color == COLOR_RED
            
            # Get the correct piece value (handle soldiers specially)
            if piece.type == TYPE_SOLDIER:
                r, c = piece.current_position
                if (is_red and r <= RIVER_ROW_TOP) or (not is_red and r >= RIVER_ROW_BOTTOM):
                    value = self.piece_values[TYPE_SOLDIER]['after_river']
                else:
                    value = self.piece_values[TYPE_SOLDIER]['before_river']
            else:
                value = self.piece_values.get(piece.type, 0)
            
            # Kiểm tra bị đe dọa
            if self._is_attacked(board, piece.current_position, is_red):
                threat_score -= value * 0.3 if is_red else value * -0.3
                
            # Kiểm tra được bảo vệ
            if self._is_defended(board, piece.current_position, is_red):
                threat_score += value * 0.2 if is_red else value * -0.2
        
        return threat_score

    def is_threatened(self, board, is_maximizing):
        """Kiểm tra xem quân cờ có bị đe dọa không"""
        player_color = COLOR_RED if is_maximizing else COLOR_BLACK
        opponent_color = COLOR_BLACK if is_maximizing else COLOR_RED
        
        for piece in board.get_pieces_by_color(player_color):
            if self._is_attacked(board, piece.current_position, is_maximizing):
                return True
        return False

    def _is_attacked(self, board, position, is_red):
        """Kiểm tra một vị trí có bị tấn công không"""
        opponent_pieces = board.black_pieces if is_red else board.red_pieces
        
        for piece in opponent_pieces:
            if position in piece.valid_positions:
                return True
        return False

    def _is_defended(self, board, position, is_red):
        """Kiểm tra một vị trí có được bảo vệ không"""
        ally_pieces = board.red_pieces if is_red else board.black_pieces
        
        for piece in ally_pieces:
            if piece.current_position != position and position in piece.valid_positions:
                return True
        return False

    def quiescence_search(self, board, alpha, beta, is_maximizing):
        """Tìm kiếm tĩnh lặng cải tiến"""
        stand_pat = self.evaluate_board(board, is_maximizing)
        
        if is_maximizing:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
        
        # Lấy các nước đi ăn quân và nước đi nguy hiểm
        moves = []
        player_color = COLOR_RED if is_maximizing else COLOR_BLACK
        
        for piece in board.get_pieces_by_color(player_color):
            if not piece.current_position:
                continue
                
            for end_pos in piece.valid_positions:
                target = board.get_piece_at(*end_pos)
                if target:
                    # Xem xét cả các nước đi có lợi
                    value_diff = self._get_piece_value(target) - self._get_piece_value(piece) * 0.6
                    if value_diff >= -50:  # Chấp nhận mất ít điểm
                        moves.append((value_diff, (piece.current_position, end_pos)))
                
                # Thêm helper method để kiểm tra chiếu tướng
                elif self._would_be_check_safe(board, piece.current_position, end_pos, player_color):
                    moves.append((100, (piece.current_position, end_pos)))  # Ưu tiên cao
        
        # Sắp xếp nước đi
        moves.sort(reverse=is_maximizing, key=lambda x: x[0])
        
        for _, move in moves:
            start_pos, end_pos = move
            board.simulator_move(start_pos, end_pos)
            
            score = self.quiescence_search(board, alpha, beta, not is_maximizing)
            
            board.undo_simulator_move(start_pos, end_pos)
            
            if is_maximizing:
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            else:
                if score <= alpha:
                    return alpha
                beta = min(beta, score)
        
        return alpha if is_maximizing else beta

    def _would_be_check_safe(self, board, start_pos, end_pos, color):
        """Phương thức an toàn để kiểm tra chiếu tướng"""
        try:
            if hasattr(board, 'would_be_check'):
                is_valid = board.simulator_move(start_pos, end_pos)
                board.undo_simulator_move(start_pos, end_pos)
                return is_valid
            
            # Fallback implementation
            temp_board = deepcopy(board)
            if temp_board.move_piece(start_pos, end_pos):
                return temp_board.is_check(color)
            return False
        except:
            return False

    def _get_piece_value(self, piece):
        """Lấy giá trị quân cờ một cách an toàn"""
        if piece.type == TYPE_SOLDIER:
            r, c = piece.current_position
            if (piece.color == COLOR_RED and r <= RIVER_ROW_TOP) or \
            (piece.color == COLOR_BLACK and r >= RIVER_ROW_BOTTOM):
                return self.piece_values[TYPE_SOLDIER]['after_river']
            return self.piece_values[TYPE_SOLDIER]['before_river']
        return self.piece_values.get(piece.type, 0)
    
    def _evaluate_mobility(self, board):
        """Đánh giá khả năng di chuyển của các quân"""
        red_mobility = sum(len(piece.valid_positions) for piece in board.red_pieces)
        black_mobility = sum(len(piece.valid_positions) for piece in board.black_pieces)
        return (red_mobility - black_mobility) / 10  # Chuẩn hóa giá trị
    
    def _evaluate_king_safety(self, board):
        """Đánh giá mức độ an toàn của tướng với xử lý lỗi"""
        try:
            # Tìm vị trí tướng đỏ
            red_king_pos = None
            for p in board.red_pieces:
                if p.type == TYPE_GENERAL and p.current_position:
                    red_king_pos = p.current_position
                    break
            
            # Tìm vị trí tướng đen
            black_king_pos = None
            for p in board.black_pieces:
                if p.type == TYPE_GENERAL and p.current_position:
                    black_king_pos = p.current_position
                    break
            
            # Nếu không tìm thấy tướng, coi như thua (điểm rất thấp)
            red_safety = -1000 if red_king_pos is None else self._calculate_king_safety(board, red_king_pos, COLOR_RED)
            black_safety = -1000 if black_king_pos is None else self._calculate_king_safety(board, black_king_pos, COLOR_BLACK)
            
            return red_safety - black_safety
        except Exception as e:
            print(f"Error evaluating king safety: {e}")
            return 0  # Trả về giá trị trung lập nếu có lỗi

    def _calculate_king_safety(self, board, king_pos, color):
        """Tính điểm an toàn cho tướng với xử lý lỗi"""
        if not king_pos:
            return -1000  # Tướng không có vị trí (đã bị bắt)
        
        try:
            safety = 0
            # Điểm cho quân phòng thủ xung quanh
            defender_count = 0
            for piece in (board.red_pieces if color == COLOR_RED else board.black_pieces):
                if piece.current_position and piece.type != TYPE_GENERAL:
                    dist = self._distance(piece.current_position, king_pos)
                    if dist <= 2:
                        defender_count += 1
                        # Quân có giá trị cao bảo vệ thì tốt hơn
                        safety += self._get_piece_value(piece) * 0.1
            
            safety += defender_count * 15
            
            # Trừ điểm nếu bị tấn công
            attacker_count = 0
            for piece in (board.black_pieces if color == COLOR_RED else board.red_pieces):
                if piece.current_position and king_pos in getattr(piece, 'valid_positions', []):
                    attacker_count += 1
                    # Quân có giá trị cao tấn công thì nguy hiểm hơn
                    safety -= self._get_piece_value(piece) * 0.2
            
            safety -= attacker_count * 25
            
            # Thêm điểm phạt nếu tướng ở vị trí nguy hiểm
            if color == COLOR_RED and king_pos[0] > 6:  # Tướng đỏ đi quá xa
                safety -= 30
            elif color == COLOR_BLACK and king_pos[0] < 3:  # Tướng đen đi quá xa
                safety -= 30
                
            return safety
        except Exception as e:
            print(f"Error calculating king safety: {e}")
            return 0
    
    def _evaluate_piece_coordination(self, board):
        """Đánh giá sự phối hợp giữa các quân"""
        red_coord = self._calculate_coordination(board.red_pieces)
        black_coord = self._calculate_coordination(board.black_pieces)
        return red_coord - black_coord
    
    def _calculate_coordination(self, pieces):
        """Tính điểm phối hợp quân"""
        coord_score = 0
        for i, p1 in enumerate(pieces):
            for p2 in pieces[i+1:]:
                if p1.current_position and p2.current_position:
                    dist = self._distance(p1.current_position, p2.current_position)
                    # Các quân gần nhau hỗ trợ tốt hơn
                    if dist <= 3:
                        coord_score += 10 - dist * 2
        return coord_score
    
    def _evaluate_pawn_structure(self, board):
        """Đánh giá cấu trúc tốt"""
        red_pawns = [p for p in board.red_pieces if p.type == TYPE_SOLDIER]
        black_pawns = [p for p in board.black_pieces if p.type == TYPE_SOLDIER]
        
        red_score = self._calculate_pawn_structure(red_pawns, COLOR_RED)
        black_score = self._calculate_pawn_structure(black_pawns, COLOR_BLACK)
        
        return red_score - black_score
    
    def _calculate_pawn_structure(self, pawns, color):
        """Tính điểm cấu trúc tốt"""
        score = 0
        pawn_cols = set()
        
        for pawn in pawns:
            if pawn.current_position:
                r, c = pawn.current_position
                pawn_cols.add(c)
                
                # Tốt qua sông có giá trị cao hơn
                if (color == COLOR_RED and r <= RIVER_ROW_TOP) or \
                   (color == COLOR_BLACK and r >= RIVER_ROW_BOTTOM):
                    score += 20
                
                # Tốt bảo vệ lẫn nhau
                protected = False
                for other in pawns:
                    if other.current_position and other.current_position != pawn.current_position:
                        o_row, o_col = other.current_position
                        if abs(o_col - c) == 1 and ((color == COLOR_RED and o_row == r + 1) or 
                                                (color == COLOR_BLACK and o_row == r - 1)):
                            protected = True
                            break
                if protected:
                    score += 15
        
        # Trừ điểm nếu tốt xếp chồng (cùng cột)
        score -= (len(pawns) - len(pawn_cols)) * 10
        return score
    
    def _distance(self, pos1, pos2):
        """Tính khoảng cách Manhattan giữa 2 vị trí"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
        # Thêm phương thức tối ưu hóa cache
    def _get_position_score(self, piece_type, row, col):
        """Lấy điểm vị trí với cache để tối ưu"""
        if not hasattr(self, '_pos_score_cache'):
            self._pos_score_cache = {}
        
        key = (piece_type, row, col)
        if key not in self._pos_score_cache:
            self._pos_score_cache[key] = self.position_scores.get(piece_type, [[0]*9]*10)[row][col]
        return self._pos_score_cache[key]
    
    def _evaluate_position(self, board):
        """Đánh giá vị trí các quân cờ"""
        position = {COLOR_RED: 0, COLOR_BLACK: 0}
        
        for piece in board.get_all_pieces():
            if not piece or piece.current_position is None:
                continue
                
            r, c = piece.current_position
            pos_score = self._get_position_score(piece.type, r, c)
            position[piece.color] += pos_score
            
            # Thưởng thêm cho tốt qua sông
            if piece.type == TYPE_SOLDIER:
                if (piece.color == COLOR_RED and r <= RIVER_ROW_TOP) or \
                   (piece.color == COLOR_BLACK and r >= RIVER_ROW_BOTTOM):
                    position[piece.color] += 15
        
        return position[COLOR_RED] - position[COLOR_BLACK]
    
    def _evaluate_material(self, board):
        """Đánh giá vật chất trên bàn cờ"""
        material = {COLOR_RED: 0, COLOR_BLACK: 0}
        
        for piece in board.get_all_pieces():
            if not piece or piece.current_position is None:
                continue
                
            # Xử lý riêng cho quân tốt (soldier)
            if piece.type == TYPE_SOLDIER:
                r, c = piece.current_position
                if (piece.color == COLOR_RED and r <= RIVER_ROW_TOP) or \
                (piece.color == COLOR_BLACK and r >= RIVER_ROW_BOTTOM):
                    # Tốt đã qua sông
                    value = self.piece_values[TYPE_SOLDIER]['after_river']
                elif (3 <= c <= 5) and ((piece.color == COLOR_RED and r >= 7) or \
                                    (piece.color == COLOR_BLACK and r <= 2)):
                    # Tốt gần cung
                    value = self.piece_values[TYPE_SOLDIER]['near_palace']
                else:
                    # Tốt chưa qua sông
                    value = self.piece_values[TYPE_SOLDIER]['before_river']
            else:
                # Các quân khác
                value = self.piece_values.get(piece.type, 0)
            
            material[piece.color] += value
        
        return material[COLOR_RED] - material[COLOR_BLACK]