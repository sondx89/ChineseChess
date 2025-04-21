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
        self._pos_score_cache = {}
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

    def _init_position_scores(self):
        base_scores = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 10, 20, 10, 0, 0, 0],
            [0, 0, 10, 20, 30, 20, 10, 0, 0],
            [0, 10, 20, 30, 40, 30, 20, 10, 0],
            [0, 20, 30, 40, 50, 40, 30, 20, 0],
            [0, 10, 20, 30, 40, 30, 20, 10, 0],
            [0, 0, 10, 20, 30, 20, 10, 0, 0],
            [0, 0, 0, 10, 20, 10, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        scores = {
            TYPE_CHARIOT: base_scores,
            TYPE_CANNON: [[int(score * 0.8) for score in row] for row in base_scores],
            TYPE_HORSE: [[int(score * 0.7) for score in row] for row in base_scores],
            TYPE_ELEPHANT: [[int(score * 0.5) for score in row] for row in base_scores],
            TYPE_ADVISOR: [[int(score * 0.3) for score in row] for row in base_scores],
            TYPE_SOLDIER: [[int(score * 0.6) for score in row] for row in base_scores],
            TYPE_GENERAL: [[0] * 9 for _ in range(10)]
        }
        for r in range(7, 10):
            for c in range(3, 6):
                scores[TYPE_GENERAL][r][c] = 20
        for r in range(0, 3):
            for c in range(3, 6):
                scores[TYPE_GENERAL][r][c] = 20
        return scores

    def get_move(self, board):
        self.simulator_board = deepcopy(board)
        self.eval_cache.clear()
        best_move = None
        best_score = -float('inf') if self.is_red else float('inf')
        alpha = -float('inf')
        beta = float('inf')
        depth = 1

        while depth <= self.depth:
            cache_key = hash(str(board.board))
            if cache_key in self.move_gen_cache:
                all_valid_moves = self.move_gen_cache[cache_key]
            else:
                all_valid_moves = self._get_all_valid_moves()
                self.move_gen_cache[cache_key] = all_valid_moves

            if not all_valid_moves:
                return None

            sorted_moves = self._sort_moves(all_valid_moves)
            aspiration_window = 50
            alpha = max(best_score - aspiration_window, -float('inf'))
            beta = min(best_score + aspiration_window, float('inf'))

            for i, move in enumerate(sorted_moves):
                start_pos, end_pos = move
                self.simulator_board.simulator_move(start_pos, end_pos)

                if i == 0:
                    score = -self.nega_scout(depth - 1, -beta, -alpha, not self.is_red)
                else:
                    score = -self.nega_scout(depth - 1, -beta, -alpha, not self.is_red)
                    if alpha < score < beta:
                        score = -self.nega_scout(depth - 1, -beta, -score, not self.is_red)

                self.simulator_board.undo_simulator_move(start_pos, end_pos)

                if (self.is_red and score > best_score) or (not self.is_red and score < best_score):
                    best_score = score
                    best_move = move

                if self.is_red:
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)

                if alpha >= beta:
                    break

            if best_score <= alpha or best_score >= beta:
                alpha = -float('inf')
                beta = float('inf')
                continue

            self._update_heuristics(move)
            depth += 1
        return best_move

    def _get_all_valid_moves(self):
        """Lấy tất cả các nước đi hợp lệ cho người chơi hiện tại."""
        all_moves = []
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = self.simulator_board.board[r][c]
                if piece and piece.color == self.is_red:
                    valid_moves = piece.get_valid_moves(self.simulator_board, (r, c))
                    all_moves.extend([(r, c), move) for move in valid_moves]
        return all_moves

    def _sort_moves(self, moves):
        """Sắp xếp các nước đi để tìm kiếm hiệu quả hơn."""
        def move_score(move):
            start_pos, end_pos = move
            target_piece = self.simulator_board.board[end_pos[0]][end_pos[1]]
            if target_piece:
                return self.piece_values[target_piece.type]  # Ưu tiên ăn quân
            else:
                return 0
        return sorted(moves, key=move_score, reverse=True)

    def _update_heuristics(self, move):
        """Cập nhật killer moves và history heuristic."""
        start_pos, end_pos = move
        self.killer_moves[self.depth].insert(0, move)
        self.killer_moves[self.depth] = self.killer_moves[self.depth][:2]  # Giữ tối đa 2 killer moves
        self.history_table[start_pos, end_pos] += 1

    def nega_scout(self, depth, alpha, beta, is_red):
        """
        Thuật toán tìm kiếm Nega-scout với alpha-beta pruning.
        """
        if depth == 0:
            return self.evaluate_board(self.simulator_board, is_red)

        # Kiểm tra transposition table
        cache_key = hash(str(self.simulator_board.board) + str(depth) + str(is_red))
        if cache_key in self.transposition_table:
            return self.transposition_table[cache_key]

        best_score = -float('inf') if is_red else float('inf')
        all_valid_moves = self._get_all_valid_moves()
        sorted_moves = self._sort_moves(all_valid_moves)

        for i, move in enumerate(sorted_moves):
            start_pos, end_pos = move
            self.simulator_board.simulator_move(start_pos, end_pos)

            if i == 0:
                score = -self.nega_scout(depth - 1, -beta, -alpha, not is_red)
            else:
                score = -self.nega_scout(depth - 1, -beta, -alpha, not is_red)
                if alpha < score < beta:
                    score = -self.nega_scout(depth - 1, -beta, -score, not is_red)

            self.simulator_board.undo_simulator_move(start_pos, end_pos)

            if is_red:
                if score > best_score:
                    best_score = score
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                beta = min(beta, score)

            if alpha >= beta:
                break

        self.transposition_table[cache_key] = best_score
        return best_score

    def evaluate_board(self, board, is_red):
        """Đánh giá điểm của bàn cờ."""
        if hash(str(board.board)) in self.eval_cache:
            return self.eval_cache[hash(str(board.board))]

        score = 0
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = board.board[r][c]
                if piece:
                    if piece.color == COLOR_RED:
                        mult = 1
                    else:
                        mult = -1
                    score += mult * self.get_piece_value(piece, r, c)

        self.eval_cache[hash(str(board.board))] = score
        return score

    def get_piece_value(self, piece, row, col):
        """Lấy giá trị của một quân cờ, có tính đến vị trí."""
        if piece.type == TYPE_SOLDIER:
            if piece.color == COLOR_RED:
                if row < 5:
                    return self.piece_values[piece.type]['before_river']
                elif 5 <= row <= 6:
                    return self.piece_values[piece.type]['after_river']
                else:
                    return self.piece_values[piece.type]['near_palace']
            else:  # Black
                if row > 4:
                    return self.piece_values[piece.type]['before_river']
                elif 3 <= row <= 4:
                    return self.piece_values[piece.type]['after_river']
                else:
                    return self.piece_values[piece.type]['near_palace']
        else:
            return self.piece_values[piece.type]
