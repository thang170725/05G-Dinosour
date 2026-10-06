import tkinter as tk
import random

# ============================================================
# CONFIG
# ============================================================
CELL = 28
GRID = 8
BOARD_X = 8
BOARD_Y = 8
BOARD_W = CELL * GRID   # 224
BOARD_H = CELL * GRID   # 224

PANEL_SCALE = 0.7        # khối trong panel nhỏ hơn khi kéo
PANEL_Y = BOARD_Y + BOARD_H + 20
PANEL_H = 4 * CELL + 12  # đủ chứa khối cao 4 ô

WIDTH = BOARD_W + BOARD_X * 2      # 240
HEIGHT = PANEL_Y + PANEL_H + 8     # 384

BG = "#1a1b2e"
BOARD_BG = "#2a2c44"
GRID_LINE = "#3a3d5a"
CELL_EMPTY = "#252740"

COLORS = [
    "#ff6b6b", "#4ecdc4", "#ffe66d", "#a8e6cf",
    "#ff8b94", "#c7ceea", "#ffa07a", "#b19cd9",
    "#7dd3fc", "#f4a261", "#98d8c8", "#f7dc6f"
]

# Shape = danh sách (row, col) — KHÔNG xoay
SHAPES = [
    [(0, 0)],                                       # dot
    [(0, 0), (0, 1)], [(0, 0), (1, 0)],             # domino
    [(0, 0), (0, 1), (0, 2)],                       # I3 ngang
    [(0, 0), (1, 0), (2, 0)],                       # I3 dọc
    [(0, 0), (1, 0), (1, 1)],                       # L3
    [(0, 0), (0, 1), (1, 0)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 1), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 0), (1, 1)],               # vuông 2x2
    [(0, 0), (0, 1), (0, 2), (1, 0)],               # J4
    [(0, 0), (0, 1), (0, 2), (1, 1)],               # T4
    [(0, 0), (0, 1), (0, 2), (1, 2)],               # L4
    [(0, 0), (0, 1), (1, 1), (1, 2)],               # S4
    [(0, 1), (0, 2), (1, 0), (1, 1)],               # Z4
    [(0, 0), (1, 0), (2, 0), (2, 1)],               # L4 dọc
    [(0, 1), (1, 1), (2, 1), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],               # I4 ngang
    [(0, 0), (1, 0), (2, 0), (3, 0)],               # I4 dọc
]


# ============================================================
# GAME
# ============================================================
class BlockPuzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("Blocks")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.board = [[None] * GRID for _ in range(GRID)]
        self.pieces = [None, None, None]
        self.score = 0
        self.game_over = False

        self.dragging = None
        self.drag_offset = (0, 0)
        self.mouse_pos = (0, 0)
        self.hover_cell = None

        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.root.bind("<KeyPress-r>", lambda e: self.restart())
        self.root.bind("<KeyPress-R>", lambda e: self.restart())

        self.new_set()
        self.draw()

    # ========================================================
    # PIECE GENERATION
    # ========================================================
    def random_piece(self):
        return {
            "shape": random.choice(SHAPES),
            "color": random.choice(COLORS)
        }

    def new_set(self):
        self.pieces = [self.random_piece() for _ in range(3)]
        self.check_game_over()

    def check_game_over(self):
        for piece in self.pieces:
            if piece is None:
                continue
            if self.piece_fits_anywhere(piece["shape"]):
                return
        self.game_over = True

    def piece_fits_anywhere(self, shape):
        for gy in range(GRID):
            for gx in range(GRID):
                if self.can_place(shape, gx, gy):
                    return True
        return False

    # ========================================================
    # BOARD LOGIC
    # ========================================================
    def can_place(self, shape, gx, gy):
        for r, c in shape:
            x, y = gx + c, gy + r
            if x < 0 or x >= GRID or y < 0 or y >= GRID:
                return False
            if self.board[y][x]:
                return False
        return True

    def place(self, piece, gx, gy):
        for r, c in piece["shape"]:
            self.board[gy + r][gx + c] = piece["color"]

    def clear_lines(self):
        full_rows = [r for r in range(GRID)
                     if all(self.board[r][c] for c in range(GRID))]
        full_cols = [c for c in range(GRID)
                     if all(self.board[r][c] for r in range(GRID))]

        for r in full_rows:
            for c in range(GRID):
                self.board[r][c] = None
        for c in full_cols:
            for r in range(GRID):
                self.board[r][c] = None

        cleared = len(full_rows) + len(full_cols)
        if cleared:
            # Clear nhiều hàng cùng lúc → điểm cao hơn
            for i in range(cleared):
                self.score += 10 * (i + 1)
        return cleared

    # ========================================================
    # SLOT HELPERS
    # ========================================================
    def get_slot_center(self, i):
        margin = 4
        slot_w = (WIDTH - margin * 2) / 3
        cx = margin + slot_w * (i + 0.5)
        cy = PANEL_Y + PANEL_H / 2
        return cx, cy

    def get_panel_piece_box(self, piece, i):
        cx, cy = self.get_slot_center(i)
        cell = CELL * PANEL_SCALE
        max_r = max(r for r, c in piece["shape"])
        max_c = max(c for r, c in piece["shape"])
        pw = (max_c + 1) * cell
        ph = (max_r + 1) * cell
        return cx - pw / 2, cy - ph / 2, pw, ph, cell

    # ========================================================
    # EVENTS
    # ========================================================
    def on_press(self, event):
        if self.game_over or self.dragging is not None:
            return
        for i in range(3):
            if self.pieces[i] is None:
                continue
            px, py, pw, ph, _ = self.get_panel_piece_box(self.pieces[i], i)
            # Padding 8px cho dễ click
            if (px - 8 <= event.x <= px + pw + 8 and
                    py - 8 <= event.y <= py + ph + 8):
                piece = self.pieces[i]
                max_r = max(r for r, c in piece["shape"])
                max_c = max(c for r, c in piece["shape"])
                full_pw = (max_c + 1) * CELL
                full_ph = (max_r + 1) * CELL
                self.dragging = i
                # Căn giữa khối theo con trỏ
                self.drag_offset = (full_pw / 2, full_ph / 2)
                self.mouse_pos = (event.x, event.y)
                self.update_hover()
                self.draw()
                return

    def on_motion(self, event):
        if self.dragging is None:
            return
        self.mouse_pos = (event.x, event.y)
        self.update_hover()
        self.draw()

    def update_hover(self):
        if self.dragging is None:
            self.hover_cell = None
            return
        piece = self.pieces[self.dragging]
        px = self.mouse_pos[0] - self.drag_offset[0]
        py = self.mouse_pos[1] - self.drag_offset[1]
        gx = round((px - BOARD_X) / CELL)
        gy = round((py - BOARD_Y) / CELL)
        if self.can_place(piece["shape"], gx, gy):
            self.hover_cell = (gx, gy)
        else:
            self.hover_cell = None

    def on_release(self, event):
        if self.dragging is None:
            return
        piece = self.pieces[self.dragging]
        px = event.x - self.drag_offset[0]
        py = event.y - self.drag_offset[1]
        gx = round((px - BOARD_X) / CELL)
        gy = round((py - BOARD_Y) / CELL)

        if self.can_place(piece["shape"], gx, gy):
            self.place(piece, gx, gy)
            self.score += 1        # +1 cho mỗi khối đặt
            self.pieces[self.dragging] = None
            self.clear_lines()

            # Hết cả 3 khối → sinh bộ mới
            if all(p is None for p in self.pieces):
                self.new_set()
            else:
                self.check_game_over()

        self.dragging = None
        self.hover_cell = None
        self.draw()

    # ========================================================
    # DRAW
    # ========================================================
    def draw(self):
        self.canvas.delete("all")
        self.draw_board()

        # Panel pieces (bỏ qua khối đang kéo)
        for i in range(3):
            if i == self.dragging or self.pieces[i] is None:
                continue
            self.draw_panel_piece(self.pieces[i], i)

        # Khối đang kéo + ghost
        if self.dragging is not None:
            piece = self.pieces[self.dragging]

            # Ghost (vẽ trước để nằm dưới khối đang kéo)
            if self.hover_cell is not None:
                gx, gy = self.hover_cell
                for r, c in piece["shape"]:
                    x1 = BOARD_X + (gx + c) * CELL
                    y1 = BOARD_Y + (gy + r) * CELL
                    self.canvas.create_rectangle(
                        x1 + 2, y1 + 2, x1 + CELL - 2, y1 + CELL - 2,
                        fill=piece["color"], outline="#ffffff",
                        width=2, stipple="gray50"
                    )

            # Khối đang kéo (theo chuột)
            px = self.mouse_pos[0] - self.drag_offset[0]
            py = self.mouse_pos[1] - self.drag_offset[1]
            for r, c in piece["shape"]:
                x1 = px + c * CELL
                y1 = py + r * CELL
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x1 + CELL - 1, y1 + CELL - 1,
                    fill=piece["color"], outline="#ffffff", width=1
                )

        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

    def draw_board(self):
        self.canvas.create_rectangle(
            BOARD_X - 3, BOARD_Y - 3,
            BOARD_X + BOARD_W + 3, BOARD_Y + BOARD_H + 3,
            fill=BOARD_BG, outline=GRID_LINE, width=2
        )
        for r in range(GRID):
            for c in range(GRID):
                x1 = BOARD_X + c * CELL
                y1 = BOARD_Y + r * CELL
                color = self.board[r][c] or CELL_EMPTY
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x1 + CELL - 1, y1 + CELL - 1,
                    fill=color, outline=""
                )

    def draw_panel_piece(self, piece, i):
        px, py, pw, ph, cell = self.get_panel_piece_box(piece, i)
        for r, c in piece["shape"]:
            x1 = px + c * cell
            y1 = py + r * cell
            self.canvas.create_rectangle(
                x1 + 1, y1 + 1, x1 + cell - 1, y1 + cell - 1,
                fill=piece["color"], outline="#ffffff", width=1
            )

    def draw_hud(self):
        self.canvas.create_text(
            WIDTH // 2, PANEL_Y - 10,
            text=f"Score: {self.score}",
            fill="#ffffff", font=("Consolas", 10, "bold")
        )

    def draw_game_over(self):
        cx = BOARD_X + BOARD_W // 2
        cy = BOARD_Y + BOARD_H // 2
        self.canvas.create_rectangle(
            BOARD_X + 10, cy - 35,
            BOARD_X + BOARD_W - 10, cy + 35,
            fill="#000000", outline="#ffffff", width=2
        )
        self.canvas.create_text(
            cx, cy - 10, text="GAME OVER",
            fill="#ff6b6b", font=("Arial", 14, "bold")
        )
        self.canvas.create_text(
            cx, cy + 15, text="Press R to restart",
            fill="#cccccc", font=("Arial", 9)
        )

    def restart(self):
        self.board = [[None] * GRID for _ in range(GRID)]
        self.score = 0
        self.game_over = False
        self.dragging = None
        self.hover_cell = None
        self.new_set()
        self.draw()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    game = BlockPuzzle(root)

    # Đặt cửa sổ ở góc trên-phải màn hình cho kín đáo
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    root.geometry(f"+{sw - WIDTH - 30}+30")

    root.mainloop()