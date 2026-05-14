class CheckersGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.size = 8
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.selected = None
        self.game_over = False
        self.won = False
        self.score = 0
        self.current_turn = 'white'
        for i in range(self.size):
            for j in range(self.size):
                if (i + j) % 2 == 1:
                    if i < 3:
                        self.board[i][j] = {'color': 'black', 'king': False}
                    elif i > 4:
                        self.board[i][j] = {'color': 'white', 'king': False}
    
    def get_board_state(self):
        #подготовка состояния доски для отправки пакетов
        return {
            'board': self.board,
            'current_turn': self.current_turn,
            'selected': self.selected,
            'game_over': self.game_over,
            'won': self.won
        }
    
    def get_valid_moves(self, row, col, color):
        #получение все возможных ходов
        piece = self.board[row][col]
        if not piece or piece['color'] != color:
            return []
        moves = []
        captures = []
        #поход наискосок
        if piece['king']:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif color == 'white':
            directions = [(-1, -1), (-1, 1)]#белые ходят вверх
        else:
            directions = [(1, -1), (1, 1)]#чёрные ходят вниз
        for dr, dc in directions:
            #сходил
            new_r, new_c = row + dr, col + dc
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                if self.board[new_r][new_c] is None:
                    moves.append((new_r, new_c))
                #съел
                elif self.board[new_r][new_c]['color'] != color:
                    jump_r, jump_c = new_r + dr, new_c + dc
                    if 0 <= jump_r < self.size and 0 <= jump_c < self.size:
                        if self.board[jump_r][jump_c] is None:
                            captures.append((jump_r, jump_c, (new_r, new_c)))
        return captures if captures else moves
    
    def has_valid_moves(self, color):
        #проверяем есть ли возможность хода
        for i in range(self.size):
            for j in range(self.size):
                piece = self.board[i][j]
                if piece and piece['color'] == color:
                    if self.get_valid_moves(i, j, color):
                        return True
        return False
    
    def make_move(self, from_pos, to_pos, color):
        #сделать ход
        if self.game_over:
            return False, "Игра окончена"
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        if not piece:
            return False, "Нет фигуры на выбранной клетке"
        if piece['color'] != color:
            return False, "Это не ваша фигура"
        valid_moves = self.get_valid_moves(from_row, from_col, color)
        #проверка обычного хода
        if (to_row, to_col) in valid_moves:
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            #в дамки
            if not piece['king']:
                if (color == 'white' and to_row == 0) or (color == 'black' and to_row == self.size - 1):
                    piece['king'] = True
            self._check_game_over()
            return True, "Ход выполнен"
        #проверка взятия
        for move in valid_moves:
            if len(move) == 3 and move[0] == to_row and move[1] == to_col:
                captured_row, captured_col = move[2]
                self.board[to_row][to_col] = piece
                self.board[from_row][from_col] = None
                self.board[captured_row][captured_col] = None
                #создание дамки
                if not piece['king']:
                    if (color == 'white' and to_row == 0) or (color == 'black' and to_row == self.size - 1):
                        piece['king'] = True
                #проверяем возможность дополнительного взятия
                more_captures = self.get_valid_moves(to_row, to_col, color)
                has_captures = any(len(m) == 3 for m in more_captures)
                if not has_captures:
                    self._check_game_over()
                return True, "Взятие выполнено"
        return False, "Недопустимый ход"
    
    def _check_game_over(self):
        #проверяем закончилась ли игра
        if not self.has_valid_moves('white'):
            self.game_over = True
            self.won = False#победа чёрных
        elif not self.has_valid_moves('black'):
            self.game_over = True
            self.won = True#победа белых
    
    def get_map_html(self):
        #создание html для отрисовки доски
        html = '<div class="checkers-board" style="display: inline-block; background: #8B4513; padding: 10px; border-radius: 10px; border: 3px solid #654321;">'
        
        for i in range(self.size):
            html += '<div class="checkers-row" style="display: flex;">'
            for j in range(self.size):
                is_dark = (i + j) % 2 == 1
                bg_color = '#3E2723' if is_dark else '#D2B48C'
                
                cell_style = f'width: 60px; height: 60px; background: {bg_color}; display: flex; align-items: center; justify-content: center; cursor: pointer;'
                
                piece = self.board[i][j]
                if piece:
                    if piece['color'] == 'white':
                        if piece['king']:
                            content = '👑'
                        else:
                            content = '⚪'
                    else:
                        if piece['king']:
                            content = '🖤'
                        else:
                            content = '⚫'
                else:
                    content = ''
                
                # Подсветка выбранной клетки
                is_selected = self.selected == (i, j)
                if is_selected:
                    cell_style += 'border: 3px solid #FFD700;'
                
                html += f'<div class="checkers-cell" data-row="{i}" data-col="{j}" style="{cell_style}">{content}</div>'
            html += '</div>'
        html += '</div>'
        
        return html