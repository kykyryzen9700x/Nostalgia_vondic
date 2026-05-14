import random


class Game2048:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.size = 4
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.add_random_tile()
        self.add_random_tile()
    
    def add_random_tile(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) 
                       if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
    
    def compress(self, row):
        new_row = [x for x in row if x != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row
    
    def merge(self, row):
        for i in range(self.size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
        return row
    
    def move_left(self):
        changed = False
        for i in range(self.size):
            original = self.board[i][:]
            self.board[i] = self.compress(self.board[i])
            self.board[i] = self.merge(self.board[i])
            self.board[i] = self.compress(self.board[i])
            if self.board[i] != original:
                changed = True
        return changed
    
    def move_right(self):
        changed = False
        for i in range(self.size):
            original = self.board[i][:]
            self.board[i] = self.board[i][::-1]
            self.board[i] = self.compress(self.board[i])
            self.board[i] = self.merge(self.board[i])
            self.board[i] = self.compress(self.board[i])
            self.board[i] = self.board[i][::-1]
            if self.board[i] != original:
                changed = True
        return changed
    
    def move_up(self):
        changed = False
        for j in range(self.size):
            original_col = [self.board[i][j] for i in range(self.size)]
            col = original_col[:]
            col = self.compress(col)
            col = self.merge(col)
            col = self.compress(col)
            if col != original_col:
                changed = True
            for i in range(self.size):
                self.board[i][j] = col[i]
        return changed
    
    def move_down(self):
        changed = False
        for j in range(self.size):
            original_col = [self.board[i][j] for i in range(self.size)]
            col = original_col[::-1]
            col = self.compress(col)
            col = self.merge(col)
            col = self.compress(col)
            col = col[::-1]
            if col != original_col:
                changed = True
            for i in range(self.size):
                self.board[i][j] = col[i]
        return changed
    
    def is_move_possible(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return True
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i][j] == self.board[i][j + 1]:
                    return True
        for i in range(self.size - 1):
            for j in range(self.size):
                if self.board[i][j] == self.board[i + 1][j]:
                    return True
        return False
    
    def check_win(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] >= 2048:
                    self.won = True
                    self.game_over = True
                    return True
        return False
    
    def move(self, direction):
        if self.game_over:
            return
        
        changed = False
        if direction == 'left':
            changed = self.move_left()
        elif direction == 'right':
            changed = self.move_right()
        elif direction == 'up':
            changed = self.move_up()
        elif direction == 'down':
            changed = self.move_down()
        
        if changed:
            self.add_random_tile()
            self.check_win()
            if not self.is_move_possible():
                self.game_over = True
    
    def get_cell_color(self, value):
        colors = {
            0: '#CDC1B4', 2: '#EEE4DA', 4: '#EDE0C8', 8: '#F2B179',
            16: '#F59563', 32: '#F67C5F', 64: '#F65E3B', 128: '#EDCF72',
            256: '#EDCC61', 512: '#EDC850', 1024: '#EDC53F', 2048: '#EDC22E'
        }
        return colors.get(value, '#3C3A32')
    
    def get_map_html(self):
        html = '<div class="game-board-2048" style="display: inline-block; background: #BBADA0; padding: 10px; border-radius: 10px;">'
        
        for i in range(self.size):
            html += '<div class="game-row" style="display: flex; justify-content: center;">'
            for j in range(self.size):
                value = self.board[i][j]
                color = self.get_cell_color(value)
                text_color = '#776E65' if value <= 4 else '#F9F6F2'
                display_value = str(value) if value > 0 else ''
                font_size = '28px' if value < 100 else '24px' if value < 1000 else '18px'
                
                html += f'''
                    <div class="game-cell-2048" style="
                        width: 70px;
                        height: 70px;
                        margin: 5px;
                        background: {color};
                        color: {text_color};
                        font-size: {font_size};
                        font-weight: bold;
                        text-align: center;
                        line-height: 70px;
                        border-radius: 8px;
                        font-family: monospace;
                    ">{display_value}</div>
                '''
            html += '</div>'
        html += '</div>'
        return html