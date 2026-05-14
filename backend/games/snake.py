import random

class SnakeGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.size = 20
        # Змейка начинается с 3 клеток
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = 'right'
        self.next_direction = 'right'
        self.food = self.random_food()
        self.score = 0
        self.game_over = False
        self.won = False
        self.move_counter = 0
    
    def random_food(self):
        while True:
            food = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            if food not in self.snake:
                return food
    
    def move(self, direction=None):
        """Движение змейки - вызывается каждый тик"""
        if self.game_over:
            return
        
        # Обновляем направление
        self.direction = self.next_direction
        
        # Вычисляем новую голову
        head = self.snake[0]
        if self.direction == 'right':
            new_head = (head[0] + 1, head[1])
        elif self.direction == 'left':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'up':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'down':
            new_head = (head[0], head[1] + 1)
        else:
            return
        
        # Проверка столкновения со стенами
        if new_head[0] < 0 or new_head[0] >= self.size or new_head[1] < 0 or new_head[1] >= self.size:
            self.game_over = True
            return
        
        # Проверка столкновения с собой (исключая хвост, который удалится)
        if new_head in self.snake[:-1]:
            self.game_over = True
            return
        
        # Добавляем новую голову
        self.snake.insert(0, new_head)
        
        # Проверка на еду
        if new_head == self.food:
            self.score += 10
            self.food = self.random_food()
            # Проверка победы (заполнено всё поле)
            if len(self.snake) == self.size * self.size:
                self.game_over = True
                self.won = True
        else:
            # Удаляем хвост, если не съели еду
            self.snake.pop()
    
    def change_direction(self, direction):
        """Изменение направления (вызывается при нажатии клавиш)"""
        opposite = {'right': 'left', 'left': 'right', 'up': 'down', 'down': 'up'}
        # Нельзя развернуться на 180 градусов
        if direction in opposite and direction != opposite.get(self.direction):
            self.next_direction = direction
    
    def get_map_html(self):
        """Генерация HTML для отображения поля: голова - большой круг, тело - квадраты"""
        html = '''<div class="snake-game-wrapper" style="display: inline-block; background: #0a0a1a; padding: 8px; border-radius: 15px; border: 3px solid #ffcc00; box-shadow: 0 0 15px rgba(255, 204, 0, 0.3);">
                        <div class="game-board snake-board" style="display: inline-block; background: #0a0a1a;">'''
        
        for i in range(self.size):
            html += '<div class="game-row snake-row" style="display: flex; margin: 0; padding: 0; line-height: 1;">'
            for j in range(self.size):
                # Уменьшенные пробелы между клетками
                cell_style = 'width: 28px; height: 28px; text-align: center; line-height: 28px; margin: 0; padding: 0; display: flex; align-items: center; justify-content: center; transition: all 0.05s ease;'
                
                if (j, i) == self.food:
                    # Еда
                    content = '🍎'
                    cell_style += ' font-size: 20px; animation: foodPulse 0.5s ease infinite alternate;'
                    cell_class = 'snake-cell snake-food'
                elif (j, i) == self.snake[0]:
                    # Голова змейки - БОЛЬШОЙ КРУГ
                    content = '●'
                    # Разные цвета головы в зависимости от направления
                    head_colors = {
                        'right': '#ff4444',
                        'left': '#44ff44', 
                        'up': '#ffaa44',
                        'down': '#44aaff'
                    }
                    color = head_colors.get(self.direction, '#ffcc00')
                    cell_style += f' font-size: 32px; color: {color}; text-shadow: 0 0 10px {color}; border-radius: 50%;'
                    cell_class = 'snake-cell snake-head'
                elif (j, i) in self.snake[1:]:
                    # Тело змейки - КВАДРАТЫ
                    content = '■'
                    # Плавный градиент для тела
                    body_index = self.snake.index((j, i))
                    opacity = 1 - (body_index / len(self.snake)) * 0.3
                    cell_style += f' font-size: 24px; color: rgba(0, 200, 100, {opacity}); text-shadow: 0 0 3px rgba(0, 255, 100, 0.5);'
                    cell_class = 'snake-cell snake-body'
                else:
                    # Пустая клетка - едва видимые точки
                    content = '·'
                    cell_style += ' font-size: 12px; color: #1a1a3a;'
                    cell_class = 'snake-cell snake-empty'
                
                html += f'<div class="{cell_class}" style="{cell_style}">{content}</div>'
            html += '</div>'
        html += '</div></div>'
        
        # Добавляем CSS анимации
        html += '''
        <style>
            @keyframes foodPulse {
                0% { transform: scale(1); opacity: 1; }
                100% { transform: scale(1.2); opacity: 0.8; }
            }
            @keyframes headGlow {
                0% { text-shadow: 0 0 5px currentColor; transform: scale(1); }
                100% { text-shadow: 0 0 20px currentColor; transform: scale(1.05); }
            }
            @keyframes bodyMove {
                0% { transform: scale(1); }
                50% { transform: scale(0.95); }
                100% { transform: scale(1); }
            }
            .snake-head {
                animation: headGlow 0.8s ease infinite alternate;
                transition: color 0.1s ease;
                font-weight: bold;
            }
            .snake-body {
                transition: all 0.05s ease;
                animation: bodyMove 0.3s ease;
            }
            .snake-food {
                transition: all 0.1s ease;
            }
            .snake-board {
                background: #0a0a1a;
            }
            .snake-row {
                margin: 0;
                padding: 0;
            }
            .snake-cell {
                font-family: monospace;
                font-weight: bold;
            }
        </style>
        '''
        return html