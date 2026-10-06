import tkinter as tk
import random


# ============================================================
# CONFIG
# ============================================================

CELL = 30
COLS = 10
ROWS = 20

WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
PREVIEW_W = 150
TOTAL_WIDTH = WIDTH + PREVIEW_W

BG = "#111111"


# ============================================================
# TETRIS PIECES
# ============================================================

SHAPES = [
    # I
    [
        [1, 1, 1, 1]
    ],

    # O
    [
        [1, 1],
        [1, 1]
    ],

    # T
    [
        [0, 1, 0],
        [1, 1, 1]
    ],

    # L
    [
        [1, 0, 0],
        [1, 1, 1]
    ],

    # J
    [
        [0, 0, 1],
        [1, 1, 1]
    ],

    # S
    [
        [0, 1, 1],
        [1, 1, 0]
    ],

    # Z
    [
        [1, 1, 0],
        [0, 1, 1]
    ],

    # Single
    [
        [1]
    ],

    # Domino
    [
        [1, 1]
    ],

    # 3-block I
    [
        [1, 1, 1]
    ],

    # 3-block L
    [
        [1, 0],
        [1, 1]
    ],

    # 3-block corner
    [
        [1, 1],
        [1, 0]
    ],

    # Plus
    [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ],

    # 5-block T
    [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0]
    ],

    # 5-block L
    [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1]
    ],

    # 5-block J
    [
        [0, 0, 1],
        [0, 0, 1],
        [1, 1, 1]
    ],

    # 5-block S
    [
        [0, 1, 1],
        [1, 1, 0],
        [1, 0, 0]
    ],

    # 5-block zigzag
    [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ],
]


COLORS = [
    "#00ffff",  # cyan
    "#ffff00",  # yellow
    "#aa00ff",  # purple
    "#ff8800",  # orange
    "#0066ff",  # blue
    "#00cc66",  # green
    "#ff3333",  # red
    "#ff66cc",  # pink
    "#66ccff",  # light blue
    "#ccff33",  # lime
    "#ff9966",  # salmon
    "#9966ff",  # violet
    "#33ff99",  # mint
    "#ff3399",  # magenta
    "#66ffcc",  # aqua
    "#ffcc33",  # gold
    "#3399ff",  # sky blue
]


# ============================================================
# TETRIS
# ============================================================

def get_piece_color(index):
    # Always return a valid color, even if more shapes are added later.
    return COLORS[index % len(COLORS)]


class Tetris:

    def __init__(self, root):

        self.root = root

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.root.title("Python Tetris")
        self.root.resizable(False, False)

        # ----------------------------------------------------
        # CANVAS
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            root,
            width=TOTAL_WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack()

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        self.info = tk.Label(
            root,
            text="Score: 0    Level: 1    Lines: 0",
            font=("Arial", 14)
        )

        self.info.pack(pady=5)

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.paused = False
        self.game_over = False

        self.after_id = None

        # ----------------------------------------------------
        # KEYBOARD
        #
        # Quan trọng:
        # Bắt phím trực tiếp trên root.
        # ----------------------------------------------------

        self.root.bind(
            "<KeyPress-p>",
            self.pause_key
        )

        self.root.bind(
            "<KeyPress-P>",
            self.pause_key
        )

        self.root.bind(
            "<KeyPress-r>",
            self.restart_key
        )

        self.root.bind(
            "<KeyPress-R>",
            self.restart_key
        )

        self.root.bind(
            "<Left>",
            self.left_key
        )

        self.root.bind(
            "<Right>",
            self.right_key
        )

        self.root.bind(
            "<Down>",
            self.down_key
        )

        self.root.bind(
            "<Up>",
            self.rotate_key
        )

        self.root.bind(
            "<space>",
            self.space_key
        )

        # ----------------------------------------------------
        # CLICK WINDOW
        #
        # Đảm bảo cửa sổ luôn nhận keyboard focus.
        # ----------------------------------------------------

        self.root.focus_force()

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        self.restart()


    # ========================================================
    # PAUSE KEY
    # ========================================================

    def pause_key(self, event=None):

        self.toggle_pause()

        # Ngăn Tkinter xử lý phím P tiếp
        return "break"


    # ========================================================
    # RESTART KEY
    # ========================================================

    def restart_key(self, event=None):

        self.restart()

        return "break"


    # ========================================================
    # LEFT KEY
    # ========================================================

    def left_key(self, event=None):

        if self.paused or self.game_over:
            return "break"

        self.move(-1, 0)

        self.draw()

        return "break"


    # ========================================================
    # RIGHT KEY
    # ========================================================

    def right_key(self, event=None):

        if self.paused or self.game_over:
            return "break"

        self.move(1, 0)

        self.draw()

        return "break"


    # ========================================================
    # DOWN KEY
    # ========================================================

    def down_key(self, event=None):

        if self.paused or self.game_over:
            return "break"

        if self.move(0, 1):

            self.score += 1

        self.update_info()

        self.draw()

        return "break"


    # ========================================================
    # ROTATE KEY
    # ========================================================

    def rotate_key(self, event=None):

        if self.paused or self.game_over:
            return "break"

        self.rotate()

        return "break"


    # ========================================================
    # SPACE KEY
    # ========================================================

    def space_key(self, event=None):

        if self.paused or self.game_over:
            return "break"

        self.hard_drop()

        return "break"


    # ========================================================
    # TOGGLE PAUSE
    # ========================================================

    def toggle_pause(self):

        if self.game_over:
            return

        # Đảo trạng thái
        self.paused = not self.paused

        # Update UI
        self.update_info()

        # Vẽ lại
        self.draw()


    # ========================================================
    # RESTART
    # ========================================================

    def restart(self):

        # ----------------------------------------------------
        # Hủy timer cũ
        # ----------------------------------------------------

        if self.after_id is not None:

            try:
                self.root.after_cancel(
                    self.after_id
                )
            except tk.TclError:
                pass

            self.after_id = None

        # ----------------------------------------------------
        # BOARD
        # ----------------------------------------------------

        self.board = [
            [0 for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.score = 0
        self.level = 1
        self.lines = 0

        self.paused = False
        self.game_over = False

        # ----------------------------------------------------
        # NEW PIECE
        # ----------------------------------------------------

        self.next_index = random.randrange(len(SHAPES))
        self.spawn_piece()

        self.update_info()

        self.draw()

        # ----------------------------------------------------
        # START TIMER
        # ----------------------------------------------------

        self.schedule_tick()

        # Đảm bảo cửa sổ nhận phím
        self.root.focus_force()


    # ========================================================
    # SCHEDULE TICK
    # ========================================================

    def schedule_tick(self):

        if self.game_over:
            return

        # ----------------------------------------------------
        # Dù Pause vẫn schedule tick.
        #
        # Nhưng tick() sẽ không làm piece rơi khi paused.
        # ----------------------------------------------------

        self.after_id = self.root.after(
            self.get_speed(),
            self.tick
        )


    # ========================================================
    # GET SPEED
    # ========================================================

    def get_speed(self):

        return max(
            80,
            600 - (self.level - 1) * 50
        )


    # ========================================================
    # GAME TICK
    # ========================================================

    def tick(self):

        self.after_id = None

        # ----------------------------------------------------
        # PAUSE
        #
        # Đây là phần quan trọng:
        #
        # Nếu paused = True
        # -> Không move
        # -> Không lock
        # -> Không clear
        #
        # Chỉ chờ tick tiếp theo.
        # ----------------------------------------------------

        if self.paused:

            self.schedule_tick()

            return

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if self.game_over:

            return

        # ----------------------------------------------------
        # MOVE DOWN
        # ----------------------------------------------------

        if not self.move(0, 1):

            self.lock_piece()

            self.clear_lines()

            self.spawn_piece()

        self.draw()

        # ----------------------------------------------------
        # NEXT TICK
        # ----------------------------------------------------

        self.schedule_tick()


    # ========================================================
    # MOVE
    # ========================================================

    def move(self, dx, dy):

        new_x = self.x + dx
        new_y = self.y + dy

        if not self.collision(
            self.piece,
            new_x,
            new_y
        ):

            self.x = new_x
            self.y = new_y

            return True

        return False


    # ========================================================
    # ROTATE
    # ========================================================

    def rotate(self):

        rotated = [
            list(row)
            for row in zip(
                *self.piece[::-1]
            )
        ]

        # Current position
        if not self.collision(
            rotated,
            self.x,
            self.y
        ):

            self.piece = rotated

            self.draw()

            return

        # Move left
        if not self.collision(
            rotated,
            self.x - 1,
            self.y
        ):

            self.x -= 1

            self.piece = rotated

            self.draw()

            return

        # Move right
        if not self.collision(
            rotated,
            self.x + 1,
            self.y
        ):

            self.x += 1

            self.piece = rotated

            self.draw()


    # ========================================================
    # HARD DROP
    # ========================================================

    def hard_drop(self):

        distance = 0

        while self.move(0, 1):

            distance += 1

        self.score += distance * 2

        self.lock_piece()

        self.clear_lines()

        self.spawn_piece()

        self.update_info()

        self.draw()


    # ========================================================
    # COLLISION
    # ========================================================

    def collision(
        self,
        piece,
        px,
        py
    ):

        for row in range(len(piece)):

            for col in range(len(piece[row])):

                if not piece[row][col]:
                    continue

                x = px + col
                y = py + row

                # Left / right
                if x < 0 or x >= COLS:

                    return True

                # Bottom
                if y >= ROWS:

                    return True

                # Existing block
                if y >= 0:

                    if self.board[y][x]:

                        return True

        return False


    # ========================================================
    # LOCK PIECE
    # ========================================================

    def lock_piece(self):

        for row in range(len(self.piece)):

            for col in range(len(self.piece[row])):

                if not self.piece[row][col]:
                    continue

                x = self.x + col
                y = self.y + row

                if 0 <= y < ROWS:

                    self.board[y][x] = self.color


    # ========================================================
    # CLEAR LINES
    # ========================================================

    def clear_lines(self):

        new_board = []

        cleared = 0

        for row in self.board:

            if all(row):

                cleared += 1

            else:

                new_board.append(row)

        # Add empty rows
        for _ in range(cleared):

            new_board.insert(
                0,
                [0 for _ in range(COLS)]
            )

        self.board = new_board

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        if cleared:

            self.lines += cleared

            points = {
                1: 100,
                2: 300,
                3: 500,
                4: 800
            }

            self.score += points.get(
                cleared,
                800
            )

            # Level up every 10 lines
            self.level = (
                self.lines // 10
            ) + 1

        self.update_info()


    # ========================================================
    # SPAWN PIECE
    # ========================================================

    def spawn_piece(self):

        # The piece shown in NEXT becomes the current piece.
        index = self.next_index

        # Immediately choose and keep the following piece visible.
        self.next_index = random.randrange(len(SHAPES))

        self.piece = [
            row[:]
            for row in SHAPES[index]
        ]

        self.color = get_piece_color(index)

        self.x = (
            COLS - len(self.piece[0])
        ) // 2

        self.y = 0

        # Game Over
        if self.collision(
            self.piece,
            self.x,
            self.y
        ):

            self.game_over = True


    # ========================================================
    # UPDATE INFO
    # ========================================================

    def update_info(self):

        if self.paused:

            text = (
                f"Score: {self.score}    "
                f"Level: {self.level}    "
                f"Lines: {self.lines}    "
                f"[PAUSED]"
            )

        else:

            text = (
                f"Score: {self.score}    "
                f"Level: {self.level}    "
                f"Lines: {self.lines}"
            )

        self.info.config(
            text=text
        )


    # ========================================================
    # DRAW
    # ========================================================

    def draw(self):

        self.canvas.delete("all")

        # ----------------------------------------------------
        # BOARD
        # ----------------------------------------------------

        for row in range(ROWS):

            for col in range(COLS):

                x1 = col * CELL
                y1 = row * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL

                # Grid
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="#222222"
                )

                # Fixed block
                if self.board[row][col]:

                    self.draw_cell(
                        col,
                        row,
                        self.board[row][col]
                    )

        # ----------------------------------------------------
        # CURRENT PIECE
        # ----------------------------------------------------

        if not self.game_over:

            for row in range(len(self.piece)):

                for col in range(len(self.piece[row])):

                    if self.piece[row][col]:

                        self.draw_cell(
                            self.x + col,
                            self.y + row,
                            self.color
                        )

        # ----------------------------------------------------
        # NEXT PIECE PANEL
        # ----------------------------------------------------

        panel_x = WIDTH
        self.canvas.create_rectangle(
            panel_x,
            0,
            TOTAL_WIDTH,
            HEIGHT,
            fill="#181818",
            outline="#444444"
        )

        self.canvas.create_text(
            panel_x + PREVIEW_W // 2,
            35,
            text="NEXT",
            fill="white",
            font=("Arial", 18, "bold")
        )

        next_piece = SHAPES[self.next_index]
        next_color = get_piece_color(self.next_index)

        preview_cell = 22
        piece_w = len(next_piece[0]) * preview_cell
        piece_h = len(next_piece) * preview_cell

        preview_x = panel_x + (PREVIEW_W - piece_w) // 2
        preview_y = 75 + (100 - piece_h) // 2

        for row in range(len(next_piece)):

            for col in range(len(next_piece[row])):

                if next_piece[row][col]:

                    x1 = preview_x + col * preview_cell
                    y1 = preview_y + row * preview_cell
                    x2 = x1 + preview_cell
                    y2 = y1 + preview_cell

                    self.canvas.create_rectangle(
                        x1 + 1,
                        y1 + 1,
                        x2 - 1,
                        y2 - 1,
                        fill=next_color,
                        outline="white"
                    )

        self.canvas.create_text(
            panel_x + PREVIEW_W // 2,
            190,
            text="NEXT PIECE",
            fill="#aaaaaa",
            font=("Arial", 10)
        )

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        controls = (
            "← →  Move\n"
            "↓     Soft drop\n"
            "↑     Rotate\n"
            "SPACE Hard drop\n"
            "P     Pause\n"
            "R     Restart"
        )

        self.canvas.create_text(
            panel_x + PREVIEW_W // 2,
            280,
            text=controls,
            fill="#cccccc",
            font=("Arial", 10),
            justify="center"
        )

        # ----------------------------------------------------
        # PAUSE SCREEN
        # ----------------------------------------------------

        if self.paused and not self.game_over:

            self.canvas.create_rectangle(
                40,
                240,
                WIDTH - 40,
                360,
                fill="#222222",
                outline="white",
                width=2
            )

            self.canvas.create_text(
                WIDTH // 2,
                280,
                text="PAUSED",
                fill="white",
                font=("Arial", 28, "bold")
            )

            self.canvas.create_text(
                WIDTH // 2,
                325,
                text="Press P to resume",
                fill="white",
                font=("Arial", 14)
            )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        if self.game_over:

            self.canvas.create_rectangle(
                40,
                240,
                WIDTH - 40,
                360,
                fill="#222222",
                outline="white",
                width=2
            )

            self.canvas.create_text(
                WIDTH // 2,
                280,
                text="GAME OVER",
                fill="white",
                font=("Arial", 28, "bold")
            )

            self.canvas.create_text(
                WIDTH // 2,
                325,
                text="Press R to restart",
                fill="white",
                font=("Arial", 14)
            )


    # ========================================================
    # DRAW CELL
    # ========================================================

    def draw_cell(
        self,
        col,
        row,
        color
    ):

        if col < 0 or col >= COLS:
            return

        if row < 0 or row >= ROWS:
            return

        x1 = col * CELL
        y1 = row * CELL

        x2 = x1 + CELL
        y2 = y1 + CELL

        self.canvas.create_rectangle(
            x1 + 1,
            y1 + 1,
            x2 - 1,
            y2 - 1,
            fill=color,
            outline="#ffffff"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    game = Tetris(root)

    root.mainloop()
