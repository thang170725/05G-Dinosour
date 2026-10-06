import tkinter as tk
import threading
import math
import time
from dataclasses import dataclass


# ============================================================
# CONFIG
# ============================================================

CELL_SIZE = 60
MARGIN = 40

DEFAULT_AI_DEPTH = 3

PIECE_TEXT = {
    'r_K': '帥',
    'r_A': '仕',
    'r_E': '相',
    'r_H': '傌',
    'r_R': '俥',
    'r_C': '炮',
    'r_P': '兵',

    'b_K': '將',
    'b_A': '士',
    'b_E': '象',
    'b_H': '馬',
    'b_R': '車',
    'b_C': '砲',
    'b_P': '卒',
}

PIECE_COLOR = {
    'r': '#d32f2f',
    'b': '#1976d2',
}

# Giá trị quân cờ
PIECE_VALUES = {
    'K': 10000,
    'R': 900,
    'C': 450,
    'H': 400,
    'E': 200,
    'A': 200,
    'P': 100,
}


# ============================================================
# MOVE
# ============================================================

@dataclass(frozen=True)
class Move:
    start: tuple
    end: tuple

    def __iter__(self):
        yield self.start
        yield self.end


# ============================================================
# XIANGQI ENGINE
# ============================================================

class XiangqiGame:

    def __init__(self):
        self.board = self.init_board()
        self.current_turn = 'r'

    # --------------------------------------------------------
    # BOARD
    # --------------------------------------------------------

    def init_board(self):
        return [
            ['b_R', 'b_H', 'b_E', 'b_A', 'b_K', 'b_A', 'b_E', 'b_H', 'b_R'],
            ['', '', '', '', '', '', '', '', ''],
            ['', 'b_C', '', '', '', '', '', 'b_C', ''],
            ['b_P', '', 'b_P', '', 'b_P', '', 'b_P', '', 'b_P'],
            ['', '', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['r_P', '', 'r_P', '', 'r_P', '', 'r_P', '', 'r_P'],
            ['', 'r_C', '', '', '', '', '', 'r_C', ''],
            ['', '', '', '', '', '', '', '', ''],
            ['r_R', 'r_H', 'r_E', 'r_A', 'r_K', 'r_A', 'r_E', 'r_H', 'r_R'],
        ]

    @staticmethod
    def copy_board(board):
        return [row[:] for row in board]

    @staticmethod
    def is_valid_pos(r, c):
        return 0 <= r < 10 and 0 <= c < 9

    @staticmethod
    def opponent(color):
        return 'b' if color == 'r' else 'r'

    # --------------------------------------------------------
    # BOARD HELPERS
    # --------------------------------------------------------

    def find_king(self, board, color):
        target = f'{color}_K'

        for r in range(10):
            for c in range(9):
                if board[r][c] == target:
                    return r, c

        return None

    def make_board_move(self, board, move):
        new_board = self.copy_board(board)

        sr, sc = move.start
        er, ec = move.end

        new_board[er][ec] = new_board[sr][sc]
        new_board[sr][sc] = ''

        return new_board

    # --------------------------------------------------------
    # PALACE
    # --------------------------------------------------------

    @staticmethod
    def in_palace(r, c, color):
        if not (3 <= c <= 5):
            return False

        if color == 'r':
            return 7 <= r <= 9

        return 0 <= r <= 2

    # --------------------------------------------------------
    # PSEUDO MOVES
    # --------------------------------------------------------

    def get_piece_moves(self, board, r, c):
        piece = board[r][c]

        if not piece:
            return []

        color = piece[0]
        piece_type = piece[2]

        moves = []

        def add_move(nr, nc):
            if not self.is_valid_pos(nr, nc):
                return False

            target = board[nr][nc]

            if target == '':
                moves.append(Move((r, c), (nr, nc)))
                return True

            if not target.startswith(color):
                moves.append(Move((r, c), (nr, nc)))

            return False

        # ====================================================
        # KING
        # ====================================================

        if piece_type == 'K':

            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ]

            for dr, dc in directions:
                nr = r + dr
                nc = c + dc

                if self.in_palace(nr, nc, color):
                    add_move(nr, nc)

        # ====================================================
        # ADVISOR
        # ====================================================

        elif piece_type == 'A':

            directions = [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
            ]

            for dr, dc in directions:
                nr = r + dr
                nc = c + dc

                if self.in_palace(nr, nc, color):
                    add_move(nr, nc)

        # ====================================================
        # ELEPHANT
        # ====================================================

        elif piece_type == 'E':

            directions = [
                (-2, -2),
                (-2, 2),
                (2, -2),
                (2, 2),
            ]

            for dr, dc in directions:

                nr = r + dr
                nc = c + dc

                if not self.is_valid_pos(nr, nc):
                    continue

                # Không được qua sông
                if color == 'r' and nr < 5:
                    continue

                if color == 'b' and nr > 4:
                    continue

                # Elephant eye
                eye_r = r + dr // 2
                eye_c = c + dc // 2

                if board[eye_r][eye_c] != '':
                    continue

                add_move(nr, nc)

        # ====================================================
        # HORSE
        # ====================================================

        elif piece_type == 'H':

            horse_moves = [
                (-2, -1, -1, 0),
                (-2, 1, -1, 0),

                (2, -1, 1, 0),
                (2, 1, 1, 0),

                (-1, -2, 0, -1),
                (1, -2, 0, -1),

                (-1, 2, 0, 1),
                (1, 2, 0, 1),
            ]

            for dr, dc, br, bc in horse_moves:

                nr = r + dr
                nc = c + dc

                if not self.is_valid_pos(nr, nc):
                    continue

                block_r = r + br
                block_c = c + bc

                if board[block_r][block_c] != '':
                    continue

                add_move(nr, nc)

        # ====================================================
        # ROOK
        # ====================================================

        elif piece_type == 'R':

            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ]

            for dr, dc in directions:

                nr = r + dr
                nc = c + dc

                while self.is_valid_pos(nr, nc):

                    if not add_move(nr, nc):
                        break

                    nr += dr
                    nc += dc

        # ====================================================
        # CANNON
        # ====================================================

        elif piece_type == 'C':

            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ]

            for dr, dc in directions:

                nr = r + dr
                nc = c + dc

                jumped = False

                while self.is_valid_pos(nr, nc):

                    target = board[nr][nc]

                    if not jumped:

                        if target == '':
                            moves.append(
                                Move((r, c), (nr, nc))
                            )
                        else:
                            jumped = True

                    else:

                        if target != '':

                            if not target.startswith(color):
                                moves.append(
                                    Move((r, c), (nr, nc))
                                )

                            break

                    nr += dr
                    nc += dc

        # ====================================================
        # PAWN
        # ====================================================

        elif piece_type == 'P':

            if color == 'r':
                forward = -1
            else:
                forward = 1

            # Đi thẳng
            add_move(r + forward, c)

            # Qua sông được đi ngang
            crossed_river = (
                (color == 'r' and r <= 4) or
                (color == 'b' and r >= 5)
            )

            if crossed_river:
                add_move(r, c - 1)
                add_move(r, c + 1)

        return moves

    # --------------------------------------------------------
    # ALL PSEUDO MOVES
    # --------------------------------------------------------

    def get_valid_moves(self, board, color):

        moves = []

        for r in range(10):
            for c in range(9):

                piece = board[r][c]

                if piece and piece.startswith(color):
                    moves.extend(
                        self.get_piece_moves(board, r, c)
                    )

        return moves

    # --------------------------------------------------------
    # ATTACK DETECTION
    # --------------------------------------------------------

    def is_square_attacked(self, board, r, c, by_color):

        # ----------------------------------------------
        # Pawn
        # ----------------------------------------------

        if by_color == 'r':
            pawn_positions = [
                (r + 1, c),
                (r, c - 1),
                (r, c + 1),
            ]
        else:
            pawn_positions = [
                (r - 1, c),
                (r, c - 1),
                (r, c + 1),
            ]

        for pr, pc in pawn_positions:

            if not self.is_valid_pos(pr, pc):
                continue

            piece = board[pr][pc]

            if piece == f'{by_color}_P':
                return True

        # ----------------------------------------------
        # Horse
        # ----------------------------------------------

        horse_patterns = [
            (-2, -1, -1, 0),
            (-2, 1, -1, 0),
            (2, -1, 1, 0),
            (2, 1, 1, 0),
            (-1, -2, 0, -1),
            (1, -2, 0, -1),
            (-1, 2, 0, 1),
            (1, 2, 0, 1),
        ]

        for dr, dc, br, bc in horse_patterns:

            hr = r + dr
            hc = c + dc

            if not self.is_valid_pos(hr, hc):
                continue

            if board[hr][hc] != f'{by_color}_H':
                continue

            block_r = r + br
            block_c = c + bc

            if board[block_r][block_c] == '':
                return True

        # ----------------------------------------------
        # King
        # ----------------------------------------------

        king_dirs = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for dr, dc in king_dirs:

            kr = r + dr
            kc = c + dc

            if not self.is_valid_pos(kr, kc):
                continue

            if board[kr][kc] == f'{by_color}_K':
                # King chỉ tấn công 4 hướng thực tế
                if dr == 0 or dc == 0:
                    return True

        # ----------------------------------------------
        # Rook / King flying general
        # ----------------------------------------------

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        for dr, dc in directions:

            nr = r + dr
            nc = c + dc

            while self.is_valid_pos(nr, nc):

                piece = board[nr][nc]

                if piece != '':

                    if piece.startswith(by_color):

                        if piece[2] == 'R':
                            return True

                        # Flying general
                        if (
                            piece[2] == 'K'
                            and dc == 0
                        ):
                            return True

                    break

                nr += dr
                nc += dc

        # ----------------------------------------------
        # Cannon
        # ----------------------------------------------

        for dr, dc in directions:

            nr = r + dr
            nc = c + dc

            screen_found = False

            while self.is_valid_pos(nr, nc):

                piece = board[nr][nc]

                if piece != '':

                    if not screen_found:
                        screen_found = True
                    else:
                        if (
                            piece.startswith(by_color)
                            and piece[2] == 'C'
                        ):
                            return True
                        break

                nr += dr
                nc += dc

        # ----------------------------------------------
        # Elephant / Advisor are handled indirectly
        # through actual move generation for legality.
        # ----------------------------------------------

        return False

    # --------------------------------------------------------
    # CHECK
    # --------------------------------------------------------

    def is_in_check(self, board, color):

        king_pos = self.find_king(board, color)

        if king_pos is None:
            return True

        kr, kc = king_pos

        opponent = self.opponent(color)

        return self.is_square_attacked(
            board,
            kr,
            kc,
            opponent
        )

    # --------------------------------------------------------
    # LEGAL MOVES
    # --------------------------------------------------------

    def get_legal_moves(self, board, color):

        legal_moves = []

        pseudo_moves = self.get_valid_moves(
            board,
            color
        )

        for move in pseudo_moves:

            new_board = self.make_board_move(
                board,
                move
            )

            # Không được để Tướng mình bị chiếu
            if not self.is_in_check(
                new_board,
                color
            ):
                legal_moves.append(move)

        return legal_moves

    # --------------------------------------------------------
    # CAPTURE VALUE
    # --------------------------------------------------------

    def captured_value(self, board, move):

        er, ec = move.end

        target = board[er][ec]

        if not target:
            return 0

        return PIECE_VALUES.get(
            target[2],
            0
        )

    # --------------------------------------------------------
    # MOVE ORDERING
    # --------------------------------------------------------

    def order_moves(self, board, moves):

        def move_score(move):

            score = 0

            target_value = self.captured_value(
                board,
                move
            )

            moving_piece = board[
                move.start[0]
            ][
                move.start[1]
            ]

            moving_value = PIECE_VALUES.get(
                moving_piece[2],
                0
            )

            # MVV-LVA
            if target_value:
                score += (
                    target_value * 10
                    - moving_value
                )

            # Ưu tiên chiếu
            new_board = self.make_board_move(
                board,
                move
            )

            enemy = self.opponent(
                moving_piece[0]
            )

            if self.is_in_check(
                new_board,
                enemy
            ):
                score += 5000

            # Ưu tiên đi về trung tâm
            center_distance = abs(
                move.end[1] - 4
            )

            score += 10 - center_distance

            return score

        return sorted(
            moves,
            key=move_score,
            reverse=True
        )

    # --------------------------------------------------------
    # POSITION SCORE
    # --------------------------------------------------------

    def positional_bonus(
        self,
        piece,
        r,
        c
    ):

        color = piece[0]
        piece_type = piece[2]

        bonus = 0

        # ----------------------------------------------
        # Pawn
        # ----------------------------------------------

        if piece_type == 'P':

            if color == 'r':

                if r <= 4:
                    bonus += 80

                # Gần phía Tướng địch
                bonus += (9 - r) * 8

            else:

                if r >= 5:
                    bonus += 80

                bonus += r * 8

            # Tốt trung tâm
            if c in (3, 4, 5):
                bonus += 15

        # ----------------------------------------------
        # Horse
        # ----------------------------------------------

        elif piece_type == 'H':

            # Tránh góc
            if 2 <= c <= 6:
                bonus += 25

            if 2 <= r <= 7:
                bonus += 20

        # ----------------------------------------------
        # Cannon
        # ----------------------------------------------

        elif piece_type == 'C':

            if c in (2, 3, 4, 5, 6):
                bonus += 15

            # Cannon thường mạnh ở trung tuyến
            if r in (4, 5):
                bonus += 20

        # ----------------------------------------------
        # Rook
        # ----------------------------------------------

        elif piece_type == 'R':

            if c in (3, 4, 5):
                bonus += 20

            if r in (3, 4, 5, 6):
                bonus += 15

        return bonus

    # --------------------------------------------------------
    # MOBILITY
    # --------------------------------------------------------

    def mobility_score(self, board, color):

        moves = self.get_legal_moves(
            board,
            color
        )

        return len(moves)

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    def evaluate(self, board):

        score = 0

        red_material = 0
        black_material = 0

        for r in range(10):
            for c in range(9):

                piece = board[r][c]

                if not piece:
                    continue

                piece_type = piece[2]

                value = PIECE_VALUES[
                    piece_type
                ]

                bonus = self.positional_bonus(
                    piece,
                    r,
                    c
                )

                total = value + bonus

                if piece.startswith('b'):
                    score += total
                    black_material += value
                else:
                    score -= total
                    red_material += value

        # ----------------------------------------------
        # Mobility
        # ----------------------------------------------

        black_mobility = len(
            self.get_valid_moves(
                board,
                'b'
            )
        )

        red_mobility = len(
            self.get_valid_moves(
                board,
                'r'
            )
        )

        score += (
            black_mobility - red_mobility
        ) * 3

        # ----------------------------------------------
        # Check bonus
        # ----------------------------------------------

        if self.is_in_check(board, 'r'):
            score += 180

        if self.is_in_check(board, 'b'):
            score -= 180

        # ----------------------------------------------
        # Material advantage amplification
        # ----------------------------------------------

        if black_material > red_material:
            score += 20

        elif red_material > black_material:
            score -= 20

        return score

    # --------------------------------------------------------
    # TERMINAL SCORE
    # --------------------------------------------------------

    def terminal_score(
        self,
        board,
        color_to_move,
        depth
    ):

        legal_moves = self.get_legal_moves(
            board,
            color_to_move
        )

        if legal_moves:
            return None

        # Không còn nước đi
        if self.is_in_check(
            board,
            color_to_move
        ):

            # Bên đang đi bị chiếu hết
            if color_to_move == 'b':
                return -1000000 - depth

            return 1000000 + depth

        # Stalemate
        return 0

    # --------------------------------------------------------
    # MINIMAX
    # --------------------------------------------------------

    def minimax(
        self,
        board,
        depth,
        alpha,
        beta,
        maximizing
    ):

        color = 'b' if maximizing else 'r'

        terminal = self.terminal_score(
            board,
            color,
            depth
        )

        if terminal is not None:
            return terminal, None

        if depth <= 0:
            return self.evaluate(board), None

        moves = self.get_legal_moves(
            board,
            color
        )

        moves = self.order_moves(
            board,
            moves
        )

        best_move = None

        # ====================================================
        # MAXIMIZING — BLACK
        # ====================================================

        if maximizing:

            best_score = -math.inf

            for move in moves:

                new_board = self.make_board_move(
                    board,
                    move
                )

                score, _ = self.minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                if score > best_score:
                    best_score = score
                    best_move = move

                alpha = max(
                    alpha,
                    best_score
                )

                if beta <= alpha:
                    break

            return best_score, best_move

        # ====================================================
        # MINIMIZING — RED
        # ====================================================

        best_score = math.inf

        for move in moves:

            new_board = self.make_board_move(
                board,
                move
            )

            score, _ = self.minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                True
            )

            if score < best_score:
                best_score = score
                best_move = move

            beta = min(
                beta,
                best_score
            )

            if beta <= alpha:
                break

        return best_score, best_move


# ============================================================
# GUI
# ============================================================

class XiangqiGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Cờ Tướng AI vs Người"
        )

        width = (
            9 * CELL_SIZE
            + 2 * MARGIN
        )

        height = (
            10 * CELL_SIZE
            + 2 * MARGIN
        )

        self.canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg="#EBC38B"
        )

        self.canvas.pack(
            padx=10,
            pady=10
        )

        # ----------------------------------------------------
        # Engine
        # ----------------------------------------------------

        self.game = XiangqiGame()

        self.ai_depth = DEFAULT_AI_DEPTH

        self.selected_pos = None
        self.valid_moves = []

        self.game_over = False
        self.ai_thinking = False

        self.last_move = None

        # ----------------------------------------------------
        # Controls
        # ----------------------------------------------------

        controls = tk.Frame(root)

        controls.pack(
            pady=(0, 10)
        )

        tk.Label(
            controls,
            text="AI Depth:"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        self.depth_var = tk.IntVar(
            value=DEFAULT_AI_DEPTH
        )

        self.depth_scale = tk.Scale(
            controls,
            from_=2,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.depth_var,
            length=150
        )

        self.depth_scale.pack(
            side=tk.LEFT
        )

        self.restart_button = tk.Button(
            controls,
            text="Chơi lại",
            command=self.restart_game
        )

        self.restart_button.pack(
            side=tk.LEFT,
            padx=10
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label = tk.Label(
            root,
            text="Lượt của Bạn (Đỏ)",
            font=("Arial", 12, "bold")
        )

        self.status_label.pack(
            pady=(0, 10)
        )

        # ----------------------------------------------------
        # Drawing
        # ----------------------------------------------------

        self.draw_board()
        self.draw_pieces()

        self.canvas.bind(
            "<Button-1>",
            self.on_click
        )

    # --------------------------------------------------------
    # BOARD DRAW
    # --------------------------------------------------------

    def draw_board(self):

        self.canvas.delete("board")

        # Horizontal lines
        for r in range(10):

            y = (
                MARGIN
                + r * CELL_SIZE
            )

            self.canvas.create_line(
                MARGIN,
                y,
                MARGIN + 8 * CELL_SIZE,
                y,
                tags="board"
            )

        # Vertical lines
        for c in range(9):

            x = (
                MARGIN
                + c * CELL_SIZE
            )

            # Trên sông
            self.canvas.create_line(
                x,
                MARGIN,
                x,
                MARGIN + 4 * CELL_SIZE,
                tags="board"
            )

            # Dưới sông
            self.canvas.create_line(
                x,
                MARGIN + 5 * CELL_SIZE,
                x,
                MARGIN + 9 * CELL_SIZE,
                tags="board"
            )

        # Palace
        self.canvas.create_line(
            MARGIN + 3 * CELL_SIZE,
            MARGIN,
            MARGIN + 5 * CELL_SIZE,
            MARGIN + 2 * CELL_SIZE,
            tags="board"
        )

        self.canvas.create_line(
            MARGIN + 5 * CELL_SIZE,
            MARGIN,
            MARGIN + 3 * CELL_SIZE,
            MARGIN + 2 * CELL_SIZE,
            tags="board"
        )

        self.canvas.create_line(
            MARGIN + 3 * CELL_SIZE,
            MARGIN + 7 * CELL_SIZE,
            MARGIN + 5 * CELL_SIZE,
            MARGIN + 9 * CELL_SIZE,
            tags="board"
        )

        self.canvas.create_line(
            MARGIN + 5 * CELL_SIZE,
            MARGIN + 7 * CELL_SIZE,
            MARGIN + 3 * CELL_SIZE,
            MARGIN + 9 * CELL_SIZE,
            tags="board"
        )

        # River
        self.canvas.create_text(
            MARGIN + 2 * CELL_SIZE,
            MARGIN + 4.5 * CELL_SIZE,
            text="SỞ HÀ",
            font=("Arial", 24, "bold"),
            tags="board"
        )

        self.canvas.create_text(
            MARGIN + 6 * CELL_SIZE,
            MARGIN + 4.5 * CELL_SIZE,
            text="HÁN GIỚI",
            font=("Arial", 24, "bold"),
            tags="board"
        )

    # --------------------------------------------------------
    # DRAW PIECES
    # --------------------------------------------------------

    def draw_pieces(self):

        self.canvas.delete("piece")
        self.canvas.delete("highlight")
        self.canvas.delete("last_move")

        # Last move
        if self.last_move:

            sr, sc = self.last_move.start
            er, ec = self.last_move.end

            for r, c in [
                (sr, sc),
                (er, ec)
            ]:

                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE

                self.canvas.create_rectangle(
                    x - 27,
                    y - 27,
                    x + 27,
                    y + 27,
                    outline="#ff9800",
                    width=3,
                    tags="last_move"
                )

        # Selected piece
        if self.selected_pos:

            r, c = self.selected_pos

            x = (
                MARGIN
                + c * CELL_SIZE
            )

            y = (
                MARGIN
                + r * CELL_SIZE
            )

            self.canvas.create_rectangle(
                x - 27,
                y - 27,
                x + 27,
                y + 27,
                outline="green",
                width=3,
                tags="highlight"
            )

            # Legal destinations
            for move in self.valid_moves:

                mr, mc = move.end

                mx = (
                    MARGIN
                    + mc * CELL_SIZE
                )

                my = (
                    MARGIN
                    + mr * CELL_SIZE
                )

                self.canvas.create_oval(
                    mx - 8,
                    my - 8,
                    mx + 8,
                    my + 8,
                    fill="green",
                    tags="highlight"
                )

        # Pieces
        for r in range(10):

            for c in range(9):

                piece = self.game.board[r][c]

                if not piece:
                    continue

                x = (
                    MARGIN
                    + c * CELL_SIZE
                )

                y = (
                    MARGIN
                    + r * CELL_SIZE
                )

                color = PIECE_COLOR[
                    piece[0]
                ]

                self.canvas.create_oval(
                    x - 22,
                    y - 22,
                    x + 22,
                    y + 22,
                    fill="#F5DEB3",
                    outline=color,
                    width=2,
                    tags="piece"
                )

                self.canvas.create_text(
                    x,
                    y,
                    text=PIECE_TEXT[piece],
                    font=(
                        "Arial",
                        20,
                        "bold"
                    ),
                    fill=color,
                    tags="piece"
                )

    # --------------------------------------------------------
    # CLICK
    # --------------------------------------------------------

    def on_click(self, event):

        if (
            self.game.current_turn != 'r'
            or self.game_over
            or self.ai_thinking
        ):
            return

        c = round(
            (event.x - MARGIN)
            / CELL_SIZE
        )

        r = round(
            (event.y - MARGIN)
            / CELL_SIZE
        )

        if not self.game.is_valid_pos(
            r,
            c
        ):
            return

        clicked_piece = (
            self.game.board[r][c]
        )

        # ----------------------------------------------------
        # Select red piece
        # ----------------------------------------------------

        if (
            clicked_piece
            and clicked_piece.startswith('r')
        ):

            self.selected_pos = (
                r,
                c
            )

            self.valid_moves = (
                self.game.get_legal_moves(
                    self.game.board,
                    'r'
                )
            )

            # Chỉ giữ nước của quân đang chọn
            self.valid_moves = [
                move
                for move in self.valid_moves
                if move.start == (
                    r,
                    c
                )
            ]

            self.draw_pieces()

            return

        # ----------------------------------------------------
        # Move selected piece
        # ----------------------------------------------------

        if self.selected_pos:

            move = Move(
                self.selected_pos,
                (r, c)
            )

            if move in self.valid_moves:

                self.make_move(move)

                self.selected_pos = None
                self.valid_moves = []

                if not self.game_over:

                    self.game.current_turn = 'b'

                    self.ai_thinking = True

                    self.status_label.config(
                        text="Máy đang suy nghĩ..."
                    )

                    self.root.title(
                        "Máy đang suy nghĩ..."
                    )

                    threading.Thread(
                        target=self.ai_turn,
                        daemon=True
                    ).start()

            else:

                self.selected_pos = None
                self.valid_moves = []

                self.draw_pieces()

    # --------------------------------------------------------
    # MAKE MOVE
    # --------------------------------------------------------

    def make_move(self, move):

        start = move.start
        end = move.end

        captured = (
            self.game.board[
                end[0]
            ][
                end[1]
            ]
        )

        self.game.board[
            end[0]
        ][
            end[1]
        ] = self.game.board[
            start[0]
        ][
            start[1]
        ]

        self.game.board[
            start[0]
        ][
            start[1]
        ] = ''

        self.last_move = move

        # King captured
        if captured and captured.endswith('_K'):

            self.game_over = True

            winner = (
                "Bạn"
                if captured.startswith('b')
                else "Máy"
            )

            self.status_label.config(
                text=f"GAME OVER — {winner} thắng!"
            )

            self.root.title(
                f"GAME OVER - {winner} WIN!"
            )

        self.draw_pieces()

    # --------------------------------------------------------
    # AI TURN
    # --------------------------------------------------------

    def ai_turn(self):

        start_time = time.time()

        depth = self.depth_var.get()

        board = self.game.copy_board(
            self.game.board
        )

        score, best_move = (
            self.game.minimax(
                board,
                depth,
                -math.inf,
                math.inf,
                True
            )
        )

        elapsed = (
            time.time()
            - start_time
        )

        if best_move:

            self.root.after(
                0,
                self.apply_ai_move,
                best_move,
                score,
                elapsed
            )

        else:

            self.root.after(
                0,
                self.ai_no_move
            )

    # --------------------------------------------------------
    # APPLY AI MOVE
    # --------------------------------------------------------

    def apply_ai_move(
        self,
        move,
        score,
        elapsed
    ):

        if self.game_over:
            return

        self.make_move(move)

        self.ai_thinking = False

        if not self.game_over:

            self.game.current_turn = 'r'

            # Nếu người chơi đang bị chiếu
            if self.game.is_in_check(
                self.game.board,
                'r'
            ):

                self.status_label.config(
                    text=(
                        f"Bạn đang bị CHIẾU! "
                        f"(AI {elapsed:.2f}s)"
                    )
                )

            else:

                self.status_label.config(
                    text=(
                        f"Lượt của Bạn "
                        f"(AI nghĩ {elapsed:.2f}s)"
                    )
                )

            self.root.title(
                "Lượt của Bạn (Quân Đỏ)"
            )

    # --------------------------------------------------------
    # AI HAS NO MOVE
    # --------------------------------------------------------

    def ai_no_move(self):

        self.ai_thinking = False

        self.game_over = True

        if self.game.is_in_check(
            self.game.board,
            'b'
        ):

            self.status_label.config(
                text="CHIẾU HẾT — Bạn thắng!"
            )

            self.root.title(
                "GAME OVER - CHIẾU HẾT! BẠN THẮNG!"
            )

        else:

            self.status_label.config(
                text="Hòa!"
            )

            self.root.title(
                "GAME OVER - HÒA"
            )

    # --------------------------------------------------------
    # RESTART
    # --------------------------------------------------------

    def restart_game(self):

        self.game = XiangqiGame()

        self.selected_pos = None
        self.valid_moves = []

        self.game_over = False
        self.ai_thinking = False

        self.last_move = None

        self.status_label.config(
            text="Lượt của Bạn (Đỏ)"
        )

        self.root.title(
            "Cờ Tướng AI vs Người"
        )

        self.draw_board()
        self.draw_pieces()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = XiangqiGUI(root)

    root.mainloop()
