class ChessGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.size = 8
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.won = False
        self.score = 0
        self.current_turn = 'white'
        #создать фигуры
        self._setup_board()
    
    def _setup_board(self):
        #раставление
        #пешки
        for i in range(self.size):
            self.board[1][i] = {'type': 'pawn', 'color': 'black'}
            self.board[6][i] = {'type': 'pawn', 'color': 'white'}
        #ладьи
        self.board[0][0] = {'type': 'rook', 'color': 'black'}
        self.board[0][7] = {'type': 'rook', 'color': 'black'}
        self.board[7][0] = {'type': 'rook', 'color': 'white'}
        self.board[7][7] = {'type': 'rook', 'color': 'white'}
        #кони
        self.board[0][1] = {'type': 'knight', 'color': 'black'}
        self.board[0][6] = {'type': 'knight', 'color': 'black'}
        self.board[7][1] = {'type': 'knight', 'color': 'white'}
        self.board[7][6] = {'type': 'knight', 'color': 'white'}
        #слоны
        self.board[0][2] = {'type': 'bishop', 'color': 'black'}
        self.board[0][5] = {'type': 'bishop', 'color': 'black'}
        self.board[7][2] = {'type': 'bishop', 'color': 'white'}
        self.board[7][5] = {'type': 'bishop', 'color': 'white'}
        #ферзи
        self.board[0][3] = {'type': 'queen', 'color': 'black'}
        self.board[7][3] = {'type': 'queen', 'color': 'white'}
        #короли
        self.board[0][4] = {'type': 'king', 'color': 'black'}
        self.board[7][4] = {'type': 'king', 'color': 'white'}
    
    def get_board_state(self):
        #проверка доски
        return {
            'board': self.board,
            'current_turn': self.current_turn,
            'selected': self.selected,
            'valid_moves': self.valid_moves,
            'game_over': self.game_over,
            'won': self.won
        }
    
    def get_piece_moves(self, row, col):
        #получение всевозможных ходов
        piece = self.board[row][col]
        if not piece:
            return []
        moves = []
        if piece['type'] == 'pawn':
            moves = self._get_pawn_moves(row, col, piece['color'])
        elif piece['type'] == 'rook':
            moves = self._get_rook_moves(row, col, piece['color'])
        elif piece['type'] == 'knight':
            moves = self._get_knight_moves(row, col, piece['color'])
        elif piece['type'] == 'bishop':
            moves = self._get_bishop_moves(row, col, piece['color'])
        elif piece['type'] == 'queen':
            moves = self._get_rook_moves(row, col, piece['color']) + self._get_bishop_moves(row, col, piece['color'])
        elif piece['type'] == 'king':
            moves = self._get_king_moves(row, col, piece['color'])
        return moves
    
    def _get_pawn_moves(self, row, col, color):
        #ходы для пешек
        moves = []
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        #ход вперёд
        new_row = row + direction
        if 0 <= new_row < self.size and self.board[new_row][col] is None:
            moves.append((new_row, col))
            #двойной ход с нача
            if row == start_row:
                new_row = row + 2 * direction
                if self.board[new_row][col] is None:
                    moves.append((new_row, col))
        #съел
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                target = self.board[new_row][new_col]
                if target and target['color'] != color:
                    moves.append((new_row, new_col))
        return moves
    
    def _get_rook_moves(self, row, col, color):
        #ход для ладьи
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, self.size):
                new_row, new_col = row + dr * i, col + dc * i
                if 0 <= new_row < self.size and 0 <= new_col < self.size:
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target['color'] != color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
                else:
                    break
        return moves
    
    def _get_knight_moves(self, row, col, color):
        #ходы коней
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                target = self.board[new_row][new_col]
                if target is None or target['color'] != color:
                    moves.append((new_row, new_col))
        return moves
    
    def _get_bishop_moves(self, row, col, color):
        #ходы слонов
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, self.size):
                new_row, new_col = row + dr * i, col + dc * i
                if 0 <= new_row < self.size and 0 <= new_col < self.size:
                    target = self.board[new_row][new_col]
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target['color'] != color:
                        moves.append((new_row, new_col))
                        break
                    else:
                        break
                else:
                    break
        return moves
    
    def _get_king_moves(self, row, col, color):
       #ходы для короля
        moves = []
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dr, dc in king_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.size and 0 <= new_col < self.size:
                target = self.board[new_row][new_col]
                if target is None or target['color'] != color:
                    moves.append((new_row, new_col))
        return moves
    
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
        valid_moves = self.get_piece_moves(from_row, from_col)
        if (to_row, to_col) in valid_moves:
            #проверка король или не король
            captured_piece = self.board[to_row][to_col]
            if captured_piece and captured_piece['type'] == 'king':
                self.game_over = True
                self.won = (color == 'white')
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            #пешка перевоплащение
            if piece['type'] == 'pawn':
                if (color == 'white' and to_row == 0) or (color == 'black' and to_row == 7):
                    piece['type'] = 'queen'
            self.valid_moves = []
            self.selected = None
            return True, "Ход выполнен"
        return False, "Недопустимый ход"
    
    def select_piece(self, row, col, color):
        #показывать возможные ходы
        piece = self.board[row][col]
        if piece and piece['color'] == color:
            self.selected = (row, col)
            self.valid_moves = self.get_piece_moves(row, col)
            return True
        return False
    
    def get_piece_symbol(self, piece):
        #получить символ фигуры
        if not piece:
            return ''
        symbols = {
            'white': {
                'king': '♔',
                'queen': '♕',
                'rook': '♖',
                'bishop': '♗',
                'knight': '♘',
                'pawn': '♙'
            },
            'black': {
                'king': '♚',
                'queen': '♛',
                'rook': '♜',
                'bishop': '♝',
                'knight': '♞',
                'pawn': '♟'
            }
        }
        
        return symbols.get(piece['color'], {}).get(piece['type'], '?')
    
    def get_map_html(self):
        """Генерация HTML для отображения доски"""
        html = '<div class="chess-board" style="display: inline-block; background: #8B4513; padding: 10px; border-radius: 10px; border: 3px solid #654321;">'
        
        # Буквы для столбцов
        html += '<div style="display: flex; justify-content: space-around; margin-bottom: 5px;">'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">A</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">B</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">C</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">D</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">E</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">F</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">G</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">H</div>'
        html += '</div>'
        
        for i in range(self.size):
            html += '<div class="chess-row" style="display: flex; align-items: center;">'
            # Цифра строки
            html += f'<div style="width: 30px; text-align: center; color: #FFF; font-size: 18px;">{self.size - i}</div>'
            
            for j in range(self.size):
                is_light = (i + j) % 2 == 0
                bg_color = '#F0D9B5' if is_light else '#B58863'
                
                cell_style = f'width: 60px; height: 60px; background: {bg_color}; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 36px;'
                
                piece = self.board[i][j]
                symbol = self.get_piece_symbol(piece)
                
                # Подсветка выбранной клетки
                if self.selected == (i, j):
                    cell_style += 'border: 3px solid #FFD700;'
                
                # Подсветка возможных ходов
                if (i, j) in self.valid_moves:
                    cell_style += 'box-shadow: inset 0 0 10px rgba(0, 255, 0, 0.5);'
                
                html += f'<div class="chess-cell" data-row="{i}" data-col="{j}" style="{cell_style}">{symbol}</div>'
            
            # Цифра строки справа
            html += f'<div style="width: 30px; text-align: center; color: #FFF; font-size: 18px;">{self.size - i}</div>'
            html += '</div>'
        
        # Буквы снизу
        html += '<div style="display: flex; justify-content: space-around; margin-top: 5px;">'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">A</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">B</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">C</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">D</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">E</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">F</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">G</div>'
        html += '<div style="width: 60px; text-align: center; color: #FFF;">H</div>'
        html += '</div>'
        
        html += '</div>'
        
        return html