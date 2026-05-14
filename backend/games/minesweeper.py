import random

class MinesweeperGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.size = 9
        self.mine_count = 10
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.revealed = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.flags = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.game_over = False
        self.won = False
        self.score = 0
        self.revealed_count = 0
        self.first_move = True
    
    def place_mines(self, first_x, first_y):
        """Расстановка мин после первого хода, исключая первую клетку"""
        # Создаём список всех клеток, кроме первой
        cells = []
        for i in range(self.size):
            for j in range(self.size):
                if not (i == first_x and j == first_y):
                    cells.append((i, j))
        
        # Случайно выбираем клетки для мин
        mine_positions = random.sample(cells, self.mine_count)
        
        # Расставляем мины
        for x, y in mine_positions:
            self.board[x][y] = -1
        
        # Подсчитываем числа вокруг мин
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == -1:
                    continue
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.size and 0 <= nj < self.size and self.board[ni][nj] == -1:
                            count += 1
                self.board[i][j] = count
    
    def reveal(self, x, y):
        """Открытие клетки (левый клик)"""
        if self.game_over or self.revealed[x][y]:
            return
        
        if self.flags[x][y]:
            return
        
        if self.first_move:
            self.first_move = False
            self.place_mines(x, y)
        
        if self.board[x][y] == -1:
            self.game_over = True
            self.won = False
            return
        
        self._reveal_cell(x, y)
    
    def _reveal_cell(self, x, y):
        """Внутренняя рекурсивная функция открытия клетки"""
        if self.revealed[x][y] or self.flags[x][y]:
            return
        
        self.revealed[x][y] = True
        self.revealed_count += 1
        self.score = self.revealed_count * 10
        
        safe_cells = self.size * self.size - self.mine_count
        if self.revealed_count == safe_cells:
            self.game_over = True
            self.won = True
        
        if self.board[x][y] == 0:
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = x + di, y + dj
                    if 0 <= ni < self.size and 0 <= nj < self.size and not self.revealed[ni][nj] and not self.flags[ni][nj]:
                        self._reveal_cell(ni, nj)
    
    def toggle_flag(self, x, y):
        """Установка/снятие флажка (правый клик или длинное нажатие)"""
        if self.game_over or self.revealed[x][y]:
            return
        
        if self.first_move:
            self.first_move = False
            self.place_mines(x, y)
        
        self.flags[x][y] = not self.flags[x][y]
    
    def auto_reveal_around(self, x, y):
        """
        Автоматическое открытие вокруг цифры,
        если количество флажков рядом равно числу на клетке
        """
        if not self.revealed[x][y] or self.board[x][y] == 0 or self.board[x][y] == -1:
            return False
        
        flag_count = 0
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = x + di, y + dj
                if 0 <= ni < self.size and 0 <= nj < self.size:
                    if self.flags[ni][nj]:
                        flag_count += 1
                    elif not self.revealed[ni][nj]:
                        neighbors.append((ni, nj))
        
        if flag_count == self.board[x][y]:
            for ni, nj in neighbors:
                if not self.flags[ni][nj] and not self.revealed[ni][nj]:
                    self.reveal(ni, nj)
            return True
        return False
    
    def get_map_html(self):
        """Генерация HTML для отображения поля"""
        html = '<div class="game-board" style="display: inline-block; background: #b0b0b0; padding: 10px; border: 3px solid #808080;">'
        
        for i in range(self.size):
            html += '<div class="game-row" style="display: flex;">'
            for j in range(self.size):
                cell_class = "game-cell"
                content = ""
                
                if self.revealed[i][j]:
                    cell_class += " revealed"
                    if self.board[i][j] == -1:
                        content = "💣"
                        cell_class += " mine"
                    elif self.board[i][j] == 0:
                        content = " "
                    else:
                        content = str(self.board[i][j])
                else:
                    if self.flags[i][j]:
                        content = "🚩"
                        cell_class += " flag"
                    else:
                        content = "■"
                        cell_class += " hidden"
                
                html += f'<div class="{cell_class}" data-x="{i}" data-y="{j}" style="width: 35px; height: 35px; text-align: center; font-size: 20px; line-height: 35px; border: 1px solid #808080; cursor: pointer; font-weight: bold;">{content}</div>'
            html += '</div>'
        html += '</div>'
        return html