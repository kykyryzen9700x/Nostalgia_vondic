import random

class SpaceInvadersGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.width = 12
        self.height = 16
        self.player_x = self.width // 2
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        self.move_counter = 0
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.shoot_cooldown = 0
        self.enemy_shoot_cooldown = 0
        self.frame_counter = 0  # Счётчик кадров для автоматического движения
        self.move_speed = 10    # Скорость движения врагов (меньше = быстрее)
        
        self.create_enemies()
    
    def create_enemies(self):
        self.enemies = []
        for row in range(3):
            for col in range(8):
                self.enemies.append({
                    'x': 2 + col,
                    'y': 2 + row,
                    'alive': True,
                    'type': row
                })
    
    def update(self):
        """Автоматическое обновление игры - вызывается каждый тик"""
        if self.game_over:
            return
        
        # Движение врагов (автоматически)
        self.move_counter += 1
        if self.move_counter >= self.move_speed:
            self.move_counter = 0
            self.move_enemies()
        
        # Движение пуль игрока
        for bullet in self.bullets[:]:
            bullet['y'] -= 1
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
            else:
                # Проверка попаданий при движении пули
                for enemy in self.enemies:
                    if enemy['alive'] and bullet['x'] == enemy['x'] and bullet['y'] == enemy['y']:
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        enemy['alive'] = False
                        self.score += 10
                        break
        
        # Движение вражеских пуль
        for bullet in self.enemy_bullets[:]:
            bullet['y'] += 1
            if bullet['y'] >= self.height:
                self.enemy_bullets.remove(bullet)
            # Проверка попадания по игроку
            elif bullet['x'] == self.player_x and bullet['y'] == self.height - 2:
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.won = False
        
        # Стрельба врагов
        if self.enemy_shoot_cooldown <= 0 and self.enemies:
            alive_enemies = [e for e in self.enemies if e['alive']]
            if alive_enemies:
                shooter = random.choice(alive_enemies)
                self.enemy_bullets.append({'x': shooter['x'], 'y': shooter['y'] + 1})
                self.enemy_shoot_cooldown = random.randint(20, 50)
        else:
            self.enemy_shoot_cooldown -= 1
        
        # Уменьшаем задержку стрельбы игрока
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Проверка столкновения врагов с игроком
        for enemy in self.enemies:
            if enemy['alive'] and enemy['y'] >= self.height - 2:
                self.game_over = True
                self.won = False
                return
        
        # Проверка победы
        alive_count = sum(1 for e in self.enemies if e['alive'])
        if alive_count == 0:
            self.game_over = True
            self.won = True
    
    def move_enemies(self):
        """Движение всех врагов"""
        if not self.enemies:
            return
        
        # Находим границы живых врагов
        alive_enemies = [e for e in self.enemies if e['alive']]
        if not alive_enemies:
            return
        
        max_x = max(e['x'] for e in alive_enemies)
        min_x = min(e['x'] for e in alive_enemies)
        
        # Проверяем нужно ли сменить направление или опуститься
        if self.enemy_direction == 1 and max_x >= self.width - 1:
            self.enemy_direction = -1
            self.enemy_move_down = True
        elif self.enemy_direction == -1 and min_x <= 0:
            self.enemy_direction = 1
            self.enemy_move_down = True
        
        # Двигаем всех врагов
        for enemy in self.enemies:
            if enemy['alive']:
                if self.enemy_move_down:
                    enemy['y'] += 1
                else:
                    enemy['x'] += self.enemy_direction
        
        self.enemy_move_down = False
    
    def move(self, direction=None):
        """Движение игрока (вызывается при нажатии клавиш)"""
        if self.game_over:
            return
        
        # Движение игрока
        if direction == 'left' and self.player_x > 0:
            self.player_x -= 1
        elif direction == 'right' and self.player_x < self.width - 1:
            self.player_x += 1
        
        # Стрельба игрока
        if direction == 'space' and self.shoot_cooldown == 0:
            self.bullets.append({'x': self.player_x, 'y': self.height - 2})
            self.shoot_cooldown = 15
        
        # Обновляем игру
        self.update()
    
    def get_map_html(self):
        html = '''
        <div class="space-invaders-game" style="display: inline-block; background: #000; padding: 10px; border-radius: 10px; border: 3px solid #0f0;">
            <div style="margin-bottom: 10px; color: #0f0; font-family: monospace; text-align: center; font-size: 14px;">
                🎯 SCORE: ''' + str(self.score) + ''' &nbsp;&nbsp;|&nbsp;&nbsp; ❤️ LIVES: ''' + '❤️' * self.lives + '''
            </div>
            <div class="invaders-board" style="background: #000;">
        '''
        
        for y in range(self.height):
            html += '<div class="invaders-row" style="display: flex; justify-content: center;">'
            for x in range(self.width):
                cell_content = ' '
                cell_style = 'width: 36px; height: 36px; text-align: center; font-size: 24px; line-height: 36px; font-family: monospace;'
                
                # Игрок
                if y == self.height - 2 and x == self.player_x and not self.game_over:
                    cell_content = '▲'
                    cell_style += 'color: #0f0; text-shadow: 0 0 5px #0f0; animation: shipGlow 0.3s ease infinite alternate;'
                # Пули игрока
                elif any(b['x'] == x and b['y'] == y for b in self.bullets):
                    cell_content = '⚡'
                    cell_style += 'color: #ff0; font-size: 18px;'
                # Вражеские пули
                elif any(b['x'] == x and b['y'] == y for b in self.enemy_bullets):
                    cell_content = '•'
                    cell_style += 'color: #f00; font-size: 20px;'
                # Враги
                else:
                    enemy_here = next((e for e in self.enemies if e['alive'] and e['x'] == x and e['y'] == y), None)
                    if enemy_here:
                        invaders = ['👾', '👽', '🛸']
                        cell_content = invaders[enemy_here['type'] % 3]
                        cell_style += 'color: #f0f; animation: enemyFloat 0.5s ease infinite alternate;'
                # Нижняя граница
                if y == self.height - 1:
                    cell_content = '▂'
                    cell_style += 'color: #0f0; font-size: 16px;'
                
                html += f'<div class="invaders-cell" style="{cell_style}">{cell_content}</div>'
            html += '</div>'
        
        html += '''
            </div>
        </div>
        <style>
            @keyframes enemyFloat {
                0% { transform: translateY(0px); text-shadow: 0 0 2px #f0f; }
                100% { transform: translateY(-3px); text-shadow: 0 0 10px #f0f; }
            }
            @keyframes shipGlow {
                0% { text-shadow: 0 0 2px #0f0; transform: scale(1); }
                100% { text-shadow: 0 0 10px #0f0; transform: scale(1.05); }
            }
            .invaders-cell {
                width: 36px;
                height: 36px;
                text-align: center;
                font-size: 24px;
                line-height: 36px;
                font-family: monospace;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .invaders-row {
                display: flex;
                justify-content: center;
            }
            .space-invaders-game {
                animation: gamePulse 2s ease infinite;
            }
            @keyframes gamePulse {
                0%, 100% { box-shadow: 0 0 5px #0f0; }
                50% { box-shadow: 0 0 15px #0f0; }
            }
        </style>
        '''
        
        return html