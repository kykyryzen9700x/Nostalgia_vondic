import random
import math
from collections import deque

class PacmanGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Увеличенная карта Pacman (21x21) - больше коридоров и пространства
        self.rows = 21
        self.cols = 21
        self.map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,0,1,1,0,1,1,0,1,0,1,0,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,1],
            [1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,1,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ]
        
        # Начальная позиция Pacman (внизу по центру)
        self.pacman_x = 10
        self.pacman_y = 16
        self.direction = 'right'
        self.next_direction = 'right'
        
        # Привидения (4 штуки) - стартуют ближе к центру
        self.ghosts = [
            {'x': 10, 'y': 9, 'color': '#FF0000', 'name': 'Blinky', 'scatter_x': 19, 'scatter_y': 1},
            {'x': 9, 'y': 10, 'color': '#FFB8FF', 'name': 'Pinky', 'scatter_x': 1, 'scatter_y': 1},
            {'x': 11, 'y': 10, 'color': '#00FFFF', 'name': 'Inky', 'scatter_x': 19, 'scatter_y': 19},
            {'x': 10, 'y': 11, 'color': '#FFB852', 'name': 'Clyde', 'scatter_x': 1, 'scatter_y': 19}
        ]
        self.ghost_mode = 'scatter'
        self.ghost_timer = 0
        self.scatter_duration = 7
        self.chase_duration = 10
        self.dots = [[True if self.map[i][j] == 0 else False for j in range(self.cols)] for i in range(self.rows)]
        self.score = 0
        self.dots_left = sum(row.count(True) for row in self.dots)
        self.game_over = False
        self.won = False
        self.move_counter = 0
    
    def can_move(self, x, y, direction):
        dx, dy = 0, 0
        if direction == 'right': dx = 1
        elif direction == 'left': dx = -1
        elif direction == 'up': dy = -1
        elif direction == 'down': dy = 1
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
            return self.map[new_y][new_x] != 1
        return False
    
    def get_valid_moves(self, x, y):
        moves = []
        for dx, dy, direction in [(0, -1, 'up'), (0, 1, 'down'), (-1, 0, 'left'), (1, 0, 'right')]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.cols and 0 <= new_y < self.rows:
                if self.map[new_y][new_x] != 1:
                    moves.append((new_x, new_y, direction))
        return moves
    
    def bfs_path(self, start_x, start_y, target_x, target_y):
        queue = deque([(start_x, start_y, [])])
        visited = {(start_x, start_y)}
        while queue:
            x, y, path = queue.popleft()
            if x == target_x and y == target_y:
                return path
            for new_x, new_y, direction in self.get_valid_moves(x, y):
                if (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append((new_x, new_y, path + [direction]))
        return None
    
    def move_ghost(self, ghost):
        if self.ghost_mode == 'scatter':
            target_x, target_y = ghost['scatter_x'], ghost['scatter_y']
        else:
            target_x, target_y = self.pacman_x, self.pacman_y
        path = self.bfs_path(ghost['x'], ghost['y'], target_x, target_y)
        if path:
            direction = path[0]
            dx, dy = 0, 0
            if direction == 'up': dy = -1
            elif direction == 'down': dy = 1
            elif direction == 'left': dx = -1
            elif direction == 'right': dx = 1
            ghost['x'] += dx
            ghost['y'] += dy
        else:
            moves = self.get_valid_moves(ghost['x'], ghost['y'])
            if moves:
                new_x, new_y, _ = random.choice(moves)
                ghost['x'], ghost['y'] = new_x, new_y
    
    def check_ghost_collision(self):
        for ghost in self.ghosts:
            if ghost['x'] == self.pacman_x and ghost['y'] == self.pacman_y:
                self.game_over = True
                self.won = False
                return True
        return False
    
    def update_ghost_mode(self):
        self.ghost_timer += 1
        if self.ghost_mode == 'scatter' and self.ghost_timer >= self.scatter_duration * 10:
            self.ghost_mode = 'chase'
            self.ghost_timer = 0
        elif self.ghost_mode == 'chase' and self.ghost_timer >= self.chase_duration * 10:
            self.ghost_mode = 'scatter'
            self.ghost_timer = 0
    
    def change_direction(self, direction):
        if direction in ['right', 'left', 'up', 'down']:
            if self.can_move(self.pacman_x, self.pacman_y, direction):
                self.next_direction = direction
                opposite = {'right': 'left', 'left': 'right', 'up': 'down', 'down': 'up'}
                if direction == opposite.get(self.direction):
                    self.direction = direction
    
    def move(self, direction=None):
        if self.game_over:
            return
        if direction and direction in ['right', 'left', 'up', 'down']:
            self.change_direction(direction)
        if self.can_move(self.pacman_x, self.pacman_y, self.next_direction):
            self.direction = self.next_direction
        dx, dy = 0, 0
        if self.direction == 'right': dx = 1
        elif self.direction == 'left': dx = -1
        elif self.direction == 'up': dy = -1
        elif self.direction == 'down': dy = 1
        new_x = self.pacman_x + dx
        new_y = self.pacman_y + dy
        if 0 <= new_x < self.cols and 0 <= new_y < self.rows and self.map[new_y][new_x] != 1:
            self.pacman_x = new_x
            self.pacman_y = new_y
        if self.dots[self.pacman_y][self.pacman_x]:
            self.dots[self.pacman_y][self.pacman_x] = False
            self.score += 10
            self.dots_left -= 1
        for ghost in self.ghosts:
            self.move_ghost(ghost)
        self.update_ghost_mode()
        self.check_ghost_collision()
        if self.dots_left == 0:
            self.game_over = True
            self.won = True
    
    def get_map_html(self):
        html = '<div class="game-board" style="display: inline-block; background: #000; padding: 8px; border-radius: 10px; border: 3px solid #2121DE;">'
        
        for i in range(self.rows):
            html += '<div class="game-row" style="display: flex;">'
            for j in range(self.cols):
                cell_content = ''
                cell_style = 'width: 25px; height: 25px; text-align: center; font-size: 16px; line-height: 25px; display: flex; align-items: center; justify-content: center;'
                ghost_here = None
                for ghost in self.ghosts:
                    if ghost['x'] == j and ghost['y'] == i:
                        ghost_here = ghost
                        break
                is_pacman = (self.pacman_x == j and self.pacman_y == i and not self.game_over)
                
                if self.map[i][j] == 1:
                    cell_content = '█'
                    cell_style += 'color: #2121DE; font-size: 14px; font-weight: bold;'
                    cell_class = 'wall'
                elif ghost_here and is_pacman:
                    cell_content = '💥'
                    cell_style += 'font-size: 18px;'
                    cell_class = 'collision'
                elif ghost_here:
                    ghost_emoji = '👻'
                    cell_content = ghost_emoji
                    cell_style += f'color: {ghost_here["color"]}; font-size: 20px; text-shadow: 0 0 5px {ghost_here["color"]};'
                    cell_class = f'ghost ghost-{ghost_here["color"]}'
                elif is_pacman:
                    arrows = {'right': '🌝', 'left': '🌝', 'up': '🌝', 'down': '🌝'}
                    cell_content = arrows.get(self.direction, '●')
                    cell_style += 'color: #ffff00; font-size: 22px; text-shadow: 0 0 10px #ffff00;'
                    cell_class = 'pacman'
                elif self.dots[i][j] and self.map[i][j] == 0:
                    cell_content = '·'
                    cell_style += 'color: #ffff00; font-size: 10px;'
                    cell_class = 'dot'
                else:
                    cell_content = ' '
                    cell_style += 'color: #000;'
                    cell_class = 'empty'
                
                html += f'<div class="game-cell {cell_class}" style="{cell_style}">{cell_content}</div>'
            html += '</div>'
        html += '</div>'
        
        html += '''
        <style>
            .ghost-red { animation: ghostFloat 0.5s ease infinite alternate; }
            .ghost-pink { animation: ghostFloat 0.6s ease 0.1s infinite alternate; }
            .ghost-cyan { animation: ghostFloat 0.55s ease 0.2s infinite alternate; }
            .ghost-orange { animation: ghostFloat 0.65s ease 0.3s infinite alternate; }
            
            @keyframes ghostFloat {
                0% { transform: translateY(-2px); }
                100% { transform: translateY(2px); }
            }
            
            @keyframes pacmanChomp {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.2); }
            }
            
            .pacman {
                animation: pacmanChomp 0.15s ease infinite;
            }
        </style>
        '''
        
        return html