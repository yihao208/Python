# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import random

# --- 常量定义 ---
# 格子状态常量
HIDDEN = 0  # 未揭开
REVEALED = 1  # 已揭开
FLAGGED = 2  # 已标记

# 游戏配置
ROWS = 9
COLS = 9
MINES = 10

# --- Cell 类 ---
class Cell:
    """
    代表游戏棋盘上的每一个格子。
    存储格子的自身属性，如坐标、是否是地雷、状态和周围地雷数。
    """
    def __init__(self, row, col):
        """
        初始化一个格子。
        :param row: 格子的行索引
        :param col: 格子的列索引
        """
        self.row = row
        self.col = col
        self.is_mine = False
        self.state = HIDDEN
        self.neighbor_mines = 0

# --- GameBoard 类 ---
class GameBoard:
    """
    代表游戏棋盘，负责管理所有格子对象和游戏的核心逻辑。
    包括地雷布置、计算数字、处理点击事件、检查胜负等。
    """
    def __init__(self, rows, cols, mines):
        """
        初始化游戏棋盘。
        :param rows: 行数
        :param cols: 列数
        :param mines: 地雷数
        """
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.game_over = False
        self.first_click = True
        self.remaining_mines = mines

    def place_mines(self, first_click_row, first_click_col):
        """
        在棋盘上随机布置地雷，确保第一次点击的位置及其周围不是地雷。
        :param first_click_row: 第一次点击的行
        :param first_click_col: 第一次点击的列
        """
        mines_placed = 0
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        safe_zone = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r, c = first_click_row + dr, first_click_col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    safe_zone.add((r, c))
        
        available_cells = list(set(all_cells) - safe_zone)
        mine_positions = random.sample(available_cells, self.mines)
        
        for r, c in mine_positions:
            self.grid[r][c].is_mine = True
            
        self.calculate_neighbor_mines()

    def calculate_neighbor_mines(self):
        """
        计算每个非地雷格子周围8个格子中的地雷总数。
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.grid[nr][nc].is_mine:
                                    count += 1
                    self.grid[r][c].neighbor_mines = count

    def reveal_cell(self, row, col):
        """
        揭开一个格子。如果是空格，则递归揭开相邻的格子。
        :param row: 要揭开的格子的行
        :param col: 要揭开的格子的列
        :return: 如果踩到地雷返回True，否则返回False
        """
        cell = self.grid[row][col]

        if cell.state != HIDDEN:
            return False

        cell.state = REVEALED

        if cell.is_mine:
            self.game_over = True
            return True

        if cell.neighbor_mines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_cell(nr, nc)
        
        return False

    def toggle_flag(self, row, col):
        """
        切换格子的标记状态（在未标记和已标记之间切换）。
        :param row: 格子的行
        :param col: 格子的列
        """
        cell = self.grid[row][col]
        if cell.state == HIDDEN:
            cell.state = FLAGGED
            self.remaining_mines -= 1
        elif cell.state == FLAGGED:
            cell.state = HIDDEN
            self.remaining_mines += 1

    def check_win(self):
        """
        检查是否所有非地雷格子都已被揭开。
        :return: 如果胜利返回True，否则返回False
        """
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_mine and cell.state != REVEALED:
                    return False
        self.game_over = True
        return True

# --- Minesweeper 主应用类 ---
class Minesweeper:
    """
    扫雷游戏的主应用程序类，负责创建和管理GUI界面。
    """
    def __init__(self, master):
        """
        初始化主窗口和游戏组件。
        :param master: tkinter的根窗口
        """
        self.master = master
        self.master.title("扫雷游戏")
        self.master.resizable(False, False)

        self.game_board = GameBoard(ROWS, COLS, MINES)

        self.info_frame = tk.Frame(master)
        self.info_frame.grid(row=0, column=0, columnspan=COLS, pady=5, sticky="ew")

        self.mine_count_var = tk.StringVar()
        self.mine_count_label = tk.Label(self.info_frame, textvariable=self.mine_count_var, font=("Arial", 14))
        self.mine_count_label.pack(side=tk.LEFT, padx=10)

        self.new_game_button = tk.Button(self.info_frame, text="新游戏", command=self.new_game, font=("Arial", 12))
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        self.timer_var = tk.StringVar()
        self.timer_label = tk.Label(self.info_frame, textvariable=self.timer_var, font=("Arial", 14))
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.buttons = []
        for r in range(ROWS):
            row_buttons = []
            for c in range(COLS):
                btn = tk.Button(master, width=2, height=1, font=("Arial", 10, "bold"))
                btn.grid(row=r + 1, column=c, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self.left_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.right_click(r, c))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        self.timer_running = False
        self.elapsed_time = 0
        self.timer_id = None

        self.new_game()

    def new_game(self):
        """
        重置并开始一局新游戏。
        """
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
        self.timer_running = False
        self.elapsed_time = 0
        self.timer_var.set("000")

        # 重置游戏棋盘逻辑
        self.game_board = GameBoard(ROWS, COLS, MINES)
        self.mine_count_var.set(f"💣 {self.game_board.remaining_mines:02d}")

        # --- 修改在这里 ---
        # 调用 update_display 来统一刷新界面，确保所有视觉属性都被重置
        self.update_display()

    def left_click(self, row, col):
        """
        处理鼠标左键点击事件。
        """
        if self.game_board.game_over:
            return

        if self.game_board.first_click:
            self.game_board.first_click = False
            self.game_board.place_mines(row, col)
            self.start_timer()

        hit_mine = self.game_board.reveal_cell(row, col)
        self.update_display()

        if hit_mine:
            self.end_game(False)
        elif self.game_board.check_win():
            self.end_game(True)

    def right_click(self, row, col):
        """
        处理鼠标右键点击事件。
        """
        if self.game_board.game_over or self.game_board.first_click:
            return

        self.game_board.toggle_flag(row, col)
        self.update_display()
        self.mine_count_var.set(f"💣 {self.game_board.remaining_mines:02d}")

    def update_display(self):
        """
        根据游戏棋盘的状态更新所有按钮的显示。
        """
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.game_board.grid[r][c]
                btn = self.buttons[r][c]

                if cell.state == HIDDEN:
                    # --- 修改在这里 ---
                    # 确保所有视觉属性都重置为默认值
                    btn.config(text="", state=tk.NORMAL, bg="SystemButtonFace", relief=tk.RAISED, fg="black")
                elif cell.state == FLAGGED:
                    btn.config(text="🚩", state=tk.NORMAL, bg="SystemButtonFace", relief=tk.RAISED, fg="black")
                elif cell.state == REVEALED:
                    btn.config(state=tk.DISABLED, relief=tk.SUNKEN)
                    if cell.is_mine:
                        btn.config(text="💣", bg="red")
                    elif cell.neighbor_mines > 0:
                        btn.config(text=str(cell.neighbor_mines), bg="SystemButtonFace")
                        colors = ["", "blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"]
                        btn.config(fg=colors[cell.neighbor_mines])
                    else:
                        btn.config(text="", bg="SystemButtonFace")
    
    def end_game(self, is_win):
        """
        游戏结束时的处理。
        :param is_win: 布尔值，True表示胜利，False表示失败
        """
        self.stop_timer()
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.game_board.grid[r][c]
                if cell.is_mine:
                    self.buttons[r][c].config(text="💣", bg="lightgray" if is_win else "red")
        
        if is_win:
            messagebox.showinfo("恭喜", "你赢了！")
        else:
            messagebox.showerror("游戏结束", "你踩到地雷了！")

    def start_timer(self):
        """
        启动计时器。
        """
        self.timer_running = True
        self.update_timer()

    def stop_timer(self):
        """
        停止计时器。
        """
        self.timer_running = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        """
        更新计时器显示。
        """
        if self.timer_running:
            self.elapsed_time += 1
            self.timer_var.set(f"{self.elapsed_time:03d}")
            self.timer_id = self.master.after(1000, self.update_timer)

# --- 主程序入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()
