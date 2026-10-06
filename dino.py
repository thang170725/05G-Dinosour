import tkinter as tk
import random


class DinoGame:
    WIDTH = 800
    HEIGHT = 300

    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Dino")
        self.root.resizable(False, False)

        # =========================
        # UI
        # =========================

        self.canvas = tk.Canvas(
            root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg="#f7f7f7",
            highlightthickness=0
        )
        self.canvas.pack()

        # =========================
        # GAME STATE
        # =========================

        self.is_jumping = False
        self.is_game_over = False

        self.score = 0.0
        self.high_score = 0

        self.base_speed = 8.0
        self.speed = self.base_speed

        # Dùng để tránh tăng speed nhiều lần ở cùng một mốc
        self.last_speed_score = 0

        # Timer IDs
        self.spawn_after_id = None
        self.game_loop_after_id = None

        # =========================
        # GROUND
        # =========================

        self.ground_y = 250

        self.canvas.create_line(
            0,
            self.ground_y,
            self.WIDTH,
            self.ground_y,
            fill="#535353",
            width=2
        )

        # =========================
        # SCORE UI
        # =========================

        self.score_text = self.canvas.create_text(
            730,
            30,
            text="00000",
            font=("Courier", 16, "bold"),
            fill="#535353"
        )

        self.hi_score_text = self.canvas.create_text(
            630,
            30,
            text="HI 00000",
            font=("Courier", 16, "bold"),
            fill="#878787"
        )

        # =========================
        # DINO
        # =========================

        self.dino_size = 40
        self.dino_x = 50

        self.dino = self.canvas.create_rectangle(
            self.dino_x,
            self.ground_y - self.dino_size,
            self.dino_x + self.dino_size,
            self.ground_y,
            fill="#535353",
            outline=""
        )

        # =========================
        # PHYSICS
        # =========================

        self.dino_vy = 0.0

        self.gravity = 1.2
        self.jump_strength = -16.0

        # =========================
        # OBSTACLES
        # =========================

        self.obstacles = []

        # =========================
        # KEYBOARD
        # =========================

        self.root.bind("<space>", self.jump)
        self.root.bind("<Up>", self.jump)

        # =========================
        # START GAME
        # =========================

        self.spawn_obstacle()
        self.game_loop()

    # =========================================================
    # JUMP
    # =========================================================

    def jump(self, event=None):
        if self.is_game_over:
            self.restart()
            return

        if not self.is_jumping:
            self.is_jumping = True
            self.dino_vy = self.jump_strength

    # =========================================================
    # RESTART
    # =========================================================

    def restart(self):
        # Hủy timer spawn cũ
        if self.spawn_after_id is not None:
            try:
                self.root.after_cancel(self.spawn_after_id)
            except tk.TclError:
                pass

            self.spawn_after_id = None

        # Hủy game loop cũ
        if self.game_loop_after_id is not None:
            try:
                self.root.after_cancel(self.game_loop_after_id)
            except tk.TclError:
                pass

            self.game_loop_after_id = None

        # Reset state
        self.is_game_over = False
        self.is_jumping = False

        self.score = 0.0
        self.speed = self.base_speed
        self.last_speed_score = 0

        self.dino_vy = 0.0

        # Xóa obstacles
        for obs in self.obstacles:
            self.canvas.delete(obs)

        self.obstacles.clear()

        # Reset Dino
        self.canvas.coords(
            self.dino,
            self.dino_x,
            self.ground_y - self.dino_size,
            self.dino_x + self.dino_size,
            self.ground_y
        )

        # Reset score
        self.canvas.itemconfig(
            self.score_text,
            text="00000"
        )

        # Xóa GAME OVER
        self.canvas.delete("gameover")

        # Bắt đầu lại
        self.spawn_obstacle()
        self.game_loop()

    # =========================================================
    # SPAWN OBSTACLE
    # =========================================================

    def spawn_obstacle(self):
        if self.is_game_over:
            return

        # Random chiều cao cây xương rồng
        h = random.randint(30, 60)

        # Random chiều rộng
        w = random.randint(15, 30)

        # Spawn bên ngoài màn hình
        obs = self.canvas.create_rectangle(
            self.WIDTH,
            self.ground_y - h,
            self.WIDTH + w,
            self.ground_y,
            fill="#535353",
            outline=""
        )

        self.obstacles.append(obs)

        # =====================================================
        # TÍNH THỜI GIAN SPAWN TIẾP THEO
        # =====================================================

        # Điểm càng cao -> spawn càng nhanh
        time_offset = max(
            200,
            800 - (self.score * 2)
        )

        # randint() bắt buộc integer
        time_offset = int(time_offset)

        next_spawn = random.randint(
            time_offset,
            time_offset + 600
        )

        self.spawn_after_id = self.root.after(
            next_spawn,
            self.spawn_obstacle
        )

    # =========================================================
    # GAME LOOP
    # =========================================================

    def game_loop(self):
        if self.is_game_over:
            return

        # =====================================================
        # 1. PHYSICS / JUMP
        # =====================================================

        if self.is_jumping:
            self.dino_vy += self.gravity

            self.canvas.move(
                self.dino,
                0,
                self.dino_vy
            )

            coords = self.canvas.coords(self.dino)

            # Chạm đất
            if coords[3] >= self.ground_y:

                self.canvas.coords(
                    self.dino,
                    self.dino_x,
                    self.ground_y - self.dino_size,
                    self.dino_x + self.dino_size,
                    self.ground_y
                )

                self.is_jumping = False
                self.dino_vy = 0.0

        # =====================================================
        # 2. SCORE
        # =====================================================

        self.score += 0.1

        score_int = int(self.score)

        formatted_score = str(score_int).zfill(5)

        self.canvas.itemconfig(
            self.score_text,
            text=formatted_score
        )

        # =====================================================
        # 3. SPEED
        # =====================================================

        # Mỗi 100 điểm tăng 0.5 speed
        # Chỉ tăng đúng 1 lần ở mỗi mốc
        speed_level = score_int // 100

        if speed_level > 0 and speed_level > self.last_speed_score:
            self.speed = self.base_speed + (speed_level * 0.5)
            self.last_speed_score = speed_level

        # =====================================================
        # 4. DINO HITBOX
        # =====================================================

        dino_coords = self.canvas.coords(
            self.dino
        )

        # =====================================================
        # 5. MOVE OBSTACLES
        # =====================================================

        for obs in self.obstacles[:]:

            self.canvas.move(
                obs,
                -self.speed,
                0
            )

            obs_coords = self.canvas.coords(obs)

            # =================================================
            # XÓA OBJECT ĐÃ RA KHỎI MÀN HÌNH
            # =================================================

            if obs_coords[2] < 0:

                self.canvas.delete(obs)

                self.obstacles.remove(obs)

                continue

            # =================================================
            # COLLISION
            # =================================================

            if self.check_collision(
                dino_coords,
                obs_coords,
                tolerance=5
            ):
                self.game_over()
                return

        # =====================================================
        # NEXT FRAME
        # =====================================================

        self.game_loop_after_id = self.root.after(
            20,
            self.game_loop
        )

    # =========================================================
    # COLLISION
    # =========================================================

    def check_collision(
        self,
        b1,
        b2,
        tolerance=0
    ):
        """
        b = [x1, y1, x2, y2]
        """

        return not (
            b1[2] - tolerance < b2[0] + tolerance
            or
            b1[0] + tolerance > b2[2] - tolerance
            or
            b1[3] - tolerance < b2[1] + tolerance
            or
            b1[1] + tolerance > b2[3] - tolerance
        )

    # =========================================================
    # GAME OVER
    # =========================================================

    def game_over(self):
        if self.is_game_over:
            return

        self.is_game_over = True

        # Hủy spawn timer
        if self.spawn_after_id is not None:
            try:
                self.root.after_cancel(
                    self.spawn_after_id
                )
            except tk.TclError:
                pass

            self.spawn_after_id = None

        # Hủy game loop
        if self.game_loop_after_id is not None:
            try:
                self.root.after_cancel(
                    self.game_loop_after_id
                )
            except tk.TclError:
                pass

            self.game_loop_after_id = None

        # =====================================================
        # HIGH SCORE
        # =====================================================

        current_score = int(self.score)

        if current_score > self.high_score:

            self.high_score = current_score

            self.canvas.itemconfig(
                self.hi_score_text,
                text=(
                    f"HI "
                    f"{str(self.high_score).zfill(5)}"
                )
            )

        # =====================================================
        # GAME OVER TEXT
        # =====================================================

        self.canvas.create_text(
            400,
            100,
            text="G A M E   O V E R",
            font=("Courier", 24, "bold"),
            fill="#535353",
            tags="gameover"
        )

        self.canvas.create_text(
            400,
            140,
            text="Press Space or Up Arrow to restart",
            font=("Courier", 12),
            fill="#878787",
            tags="gameover"
        )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = DinoGame(root)

    root.mainloop()