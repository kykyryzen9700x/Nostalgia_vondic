import random


class FlappyBirdGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.width = 20
        self.height = 15
        self.bird_x = 5
        self.bird_y = self.height // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_power = -2
        self.pipe_width = 3
        self.pipe_gap = 5
        self.pipe_spacing = 10
        self.pipe_speed = 1
        self.pipes = []
        self.score = 0
        self.frame_counter = 0
        self.game_over = False
        self.won = False
    
    def add_pipe(self):
        gap_y = random.randint(2, self.height - self.pipe_gap - 2)
        self.pipes.append({
            'x': self.width,
            'gap_y': gap_y
        })
    
    def update(self):
        if self.game_over:
            return
        
        self.velocity += self.gravity
        self.bird_y += self.velocity
        
        if self.bird_y <= 0 or self.bird_y >= self.height - 1:
            self.game_over = True
            return
        
        for pipe in self.pipes[:]:
            pipe['x'] -= self.pipe_speed
            
            if (pipe['x'] <= self.bird_x + 1 <= pipe['x'] + self.pipe_width):
                if (self.bird_y < pipe['gap_y'] or 
                    self.bird_y > pipe['gap_y'] + self.pipe_gap):
                    self.game_over = True
                    return
            if pipe['x'] + self.pipe_width < 0:
                self.pipes.remove(pipe)
                self.score += 10
        
        self.frame_counter += 1
        if (self.frame_counter >= self.pipe_spacing and 
            (not self.pipes or self.pipes[-1]['x'] < self.width - self.pipe_spacing)):
            self.add_pipe()
            self.frame_counter = 0
    
    def jump(self):
        if not self.game_over:
            self.velocity = self.jump_power
    
    def move(self, direction=None):
        if direction == 'up' and not self.game_over:
            self.jump()
        self.update()
    
    def get_map_html(self):
        html = '<div class="game-board" style="display: inline-block; background: #87CEEB; padding: 10px; border-radius: 10px;">'
        
        for y in range(self.height):
            html += '<div class="game-row" style="display: flex;">'
            for x in range(self.width):
                if x == self.bird_x and y == int(self.bird_y):
                    content = '🐦'
                elif any(pipe['x'] <= x <= pipe['x'] + self.pipe_width for pipe in self.pipes):
                    pipe = next((p for p in self.pipes if p['x'] <= x <= p['x'] + self.pipe_width), None)
                    if pipe and (y < pipe['gap_y'] or y > pipe['gap_y'] + self.pipe_gap):
                        content = '🟩'
                    else:
                        content = '⬛'
                else:
                    content = '⬛' if (x + y) % 2 == 0 else '⬛'
                
                html += f'<div class="game-cell" style="width: 35px; height: 35px; text-align: center; font-size: 22px; line-height: 35px;">{content}</div>'
            html += '</div>'
        html += '</div>'
        return html