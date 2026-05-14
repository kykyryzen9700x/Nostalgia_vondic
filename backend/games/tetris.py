import random


class TetrisGame:
    SHAPES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 1, 0], [0, 1, 1]]
    ]
    
    COLORS = ['#00FFFF', '#FFFF00', '#AA00FF', '#FFA500', '#0000FF', '#00FF00', '#FF0000']
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.width = 10
        self.height = 20
        self.board = [[0] * self.width for _ in range(self.height)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.won = False
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_color = 0
        self.next_piece = None
        self.next_color = 0
        self.frame_counter = 0
        self.fall_speed = 30
        self.spawn_new_piece()
        self.spawn_next_piece()
    
    def random_piece(self):
        idx = random.randint(0, len(self.SHAPES) - 1)
        shape = [row[:] for row in self.SHAPES[idx]]
        return shape, idx
    
    def spawn_new_piece(self):
        if self.next_piece is None:
            self.current_piece, self.current_color = self.random_piece()
        else:
            self.current_piece = self.next_piece
            self.current_color = self.next_color
        
        self.current_x = self.width // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        if self.collision():
            self.game_over = True
    
    def spawn_next_piece(self):
        self.next_piece, self.next_color = self.random_piece()
    
    def collision(self):
        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_x + j
                    y = self.current_y + i
                    if (x < 0 or x >= self.width or 
                        y >= self.height or
                        (y >= 0 and self.board[y][x])):
                        return True
        return False
    
    def merge_piece(self):
        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_x + j
                    y = self.current_y + i
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.board[y][x] = self.current_color + 1
        
        self.clear_lines()
        self.spawn_new_piece()
        self.spawn_next_piece()
    
    def clear_lines(self):
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(self.board[y]):
                del self.board[y]
                self.board.insert(0, [0] * self.width)
                lines_cleared += 1
            else:
                y -= 1
        
        if lines_cleared > 0:
            points = [0, 100, 300, 500, 800]
            self.score += points[min(lines_cleared, 4)]
            self.lines_cleared += lines_cleared
            self.level = 1 + (self.lines_cleared // 10)
            self.fall_speed = max(5, 30 - (self.level - 1) * 2)
    
    def rotate_piece(self):
        rotated = [list(row)[::-1] for row in zip(*self.current_piece)]
        original = self.current_piece
        self.current_piece = rotated
        
        if self.collision():
            self.current_piece = original
    
    def move_left(self):
        self.current_x -= 1
        if self.collision():
            self.current_x += 1
    
    def move_right(self):
        self.current_x += 1
        if self.collision():
            self.current_x -= 1
    
    def move_down(self):
        self.current_y += 1
        if self.collision():
            self.current_y -= 1
            self.merge_piece()
    
    def hard_drop(self):
        while not self.collision():
            self.current_y += 1
        self.current_y -= 1
        self.merge_piece()
    
    def update(self):
        if self.game_over:
            return
        
        self.frame_counter += 1
        if self.frame_counter >= self.fall_speed:
            self.frame_counter = 0
            self.move_down()
    
    def move(self, direction):
        if self.game_over:
            return
        
        if direction == 'up':
            self.rotate_piece()
        elif direction == 'left':
            self.move_left()
        elif direction == 'right':
            self.move_right()
        elif direction == 'down':
            self.move_down()
        elif direction == 'space':
            self.hard_drop()
        
        self.update()
    
    def get_map_html(self):
        html = '<div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">'
        
        html += '<div class="game-board" style="background: #000; padding: 5px; border-radius: 10px;">'
        for y in range(self.height):
            html += '<div class="game-row" style="display: flex;">'
            for x in range(self.width):
                value = self.board[y][x]
                is_active = False
                
                if self.current_piece and not self.game_over:
                    for i, row in enumerate(self.current_piece):
                        for j, cell in enumerate(row):
                            if (cell and 
                                self.current_x + j == x and 
                                self.current_y + i == y):
                                value = self.current_color + 1
                                is_active = True
                                break
                        if is_active:
                            break
                
                if value > 0:
                    color = self.COLORS[value - 1]
                    content = '■'
                else:
                    color = '#111'
                    content = '·'
                
                html += f'<div class="game-cell" style="width: 30px; height: 30px; background: {color}; color: {color}; text-align: center; font-size: 20px; line-height: 30px;">{content}</div>'
            html += '</div>'
        html += '</div>'
        
        html += '<div style="background: #000; padding: 15px; border-radius: 10px; text-align: center;">'
        html += '<h3 style="color: #fff; margin-bottom: 15px;">СЛЕДУЮЩАЯ</h3>'
        
        if self.next_piece:
            preview_height = len(self.next_piece)
            preview_width = len(self.next_piece[0])
            html += '<div style="display: inline-block;">'
            for i in range(preview_height):
                html += '<div style="display: flex; justify-content: center;">'
                for j in range(preview_width):
                    if self.next_piece[i][j]:
                        color = self.COLORS[self.next_color]
                        content = '■'
                    else:
                        color = '#111'
                        content = '·'
                    html += f'<div style="width: 30px; height: 30px; background: {color}; color: {color}; margin: 2px;">{content}</div>'
                html += '</div>'
            html += '</div>'
        
        html += f'<div style="color: #fff; margin-top: 20px;">УРОВЕНЬ: {self.level}</div>'
        html += '<div style="color: #ffcc00; margin-top: 10px;">ПРОБЕЛ - БЫСТРОЕ ПАДЕНИЕ</div>'
        html += '</div>'
        
        html += '</div>'
        return html