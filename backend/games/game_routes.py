from flask import Blueprint, render_template, request, jsonify, session, redirect
from backend.games.game_manager import GameManager
from functools import wraps

game_bp = Blueprint('games', __name__)
game_manager = GameManager()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Требуется авторизация', 'redirect': '/login'}), 401
        return f(*args, **kwargs)
    return decorated_function


@game_bp.route('/game/<game_name>')
def game_page(game_name):
    """Страница игры - проверяем авторизацию"""
    if 'user_id' not in session:
        return redirect('/login')
    
    if game_name not in GameManager.GAMES:
        return redirect('/')
    
    templates = {
        'flappy': 'game_flappy.html',
        '2048': 'game_2048.html',
        'tetris': 'game_tetris.html',
        'checkers': 'game_multiplayer.html',
        'chess': 'game_multiplayer.html',
        'space_invaders': 'game_space_invaders.html'
    }
    
    template = templates.get(game_name, 'game.html')
    
    return render_template(template, 
                         game_name=game_name.upper(), 
                         game_type=game_name)


@game_bp.route('/api/game/<game_type>/lobby', methods=['POST'])
@login_required
def create_or_join_lobby(game_type):
    """Создать лобби или подключиться к нему"""
    if game_type not in GameManager.MULTIPLAYER_GAMES:
        return jsonify({'error': 'Not a multiplayer game'}), 400
    
    data = request.json
    action = data.get('action')
    
    user_id = str(session.get('user_id'))
    nickname = session.get('nickname', 'User')
    
    if action == 'create':
        lobby_id = game_manager.create_lobby(game_type, user_id, nickname)
        lobby_info = game_manager.get_lobby_info(lobby_id)
        return jsonify({'lobby_id': lobby_id, 'lobby': lobby_info})
    
    elif action == 'join':
        lobby_id = data.get('lobby_id')
        success, message = game_manager.join_lobby(lobby_id, user_id, nickname)
        if success:
            lobby_info = game_manager.get_lobby_info(lobby_id)
            return jsonify({'success': True, 'lobby': lobby_info})
        else:
            return jsonify({'success': False, 'error': message}), 400
    
    return jsonify({'error': 'Unknown action'}), 400


@game_bp.route('/api/game/<game_type>/lobby/<lobby_id>', methods=['GET'])
@login_required
def get_lobby_status(game_type, lobby_id):
    """Получить статус лобби"""
    lobby_info = game_manager.get_lobby_info(lobby_id)
    if lobby_info:
        return jsonify({'lobby': lobby_info})
    return jsonify({'error': 'Lobby not found'}), 404


@game_bp.route('/api/game/<game_type>', methods=['POST'])
@login_required
def game_api(game_type):
    """API для игр - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    if game_type not in GameManager.GAMES:
        return jsonify({'error': 'Unknown game'}), 400
    
    data = request.json
    action = data.get('action')
    user_id = str(session.get('user_id'))
    nickname = session.get('nickname', 'User')
    
    try:
        # Для мультиплеерных игр всегда ищем игру через лобби
        if game_type in GameManager.MULTIPLAYER_GAMES:
            # Находим лобби, где участвует этот пользователь
            lobby = None
            lobby_id = None
            for l_id, l in game_manager._lobbies.items():
                if l['game_type'] == game_type:
                    if l['host_user_id'] == user_id or l['guest_user_id'] == user_id:
                        lobby = l
                        lobby_id = l_id
                        break
            
            if not lobby and action not in ['get_state']:
                return jsonify({'error': 'Вы не в игре'}), 400
            
            if action == 'get_state':
                if lobby:
                    game = lobby['game']
                    state = game_manager.get_game_state(game)
                    state['current_turn'] = lobby['current_turn']
                    state['player_color'] = 'white' if lobby['host_user_id'] == user_id else 'black'
                    state['host_nickname'] = lobby['host_nickname']
                    state['guest_nickname'] = lobby['guest_nickname']
                    return jsonify(state)
                else:
                    return jsonify({'error': 'Not in lobby', 'game_over': False})
            
            elif action == 'make_move':
                game = lobby['game']
                
                # Определяем цвет игрока
                if lobby['host_user_id'] == user_id:
                    player_color = 'white'
                elif lobby['guest_user_id'] == user_id:
                    player_color = 'black'
                else:
                    return jsonify({'error': 'Вы не в этой игре'}), 400
                
                # Проверяем очередь хода
                if lobby['current_turn'] != player_color:
                    return jsonify({
                        'success': False,
                        'message': 'Сейчас не ваш ход',
                        'map_html': game.get_map_html(),
                        'current_turn': lobby['current_turn'],
                        'player_color': player_color
                    })
                
                from_pos = data.get('from')
                to_pos = data.get('to')
                
                if not from_pos or not to_pos:
                    return jsonify({'error': 'Не указаны координаты'}), 400
                
                from_pos = tuple(from_pos)
                to_pos = tuple(to_pos)
                
                # Делаем ход напрямую в игре лобби
                success, message = game.make_move(from_pos, to_pos, player_color)
                
                if success:
                    # Переключаем ход
                    lobby['current_turn'] = 'black' if lobby['current_turn'] == 'white' else 'white'
                
                state = game_manager.get_game_state(game)
                state['success'] = success
                state['message'] = message
                state['current_turn'] = lobby['current_turn']
                state['player_color'] = player_color
                
                return jsonify(state)
            
            elif action == 'select' and game_type == 'chess':
                game = lobby['game']
                
                if lobby['host_user_id'] == user_id:
                    player_color = 'white'
                elif lobby['guest_user_id'] == user_id:
                    player_color = 'black'
                else:
                    return jsonify({'error': 'Вы не в этой игре'}), 400
                
                row = data.get('row')
                col = data.get('col')
                
                if row is not None and col is not None:
                    game.select_piece(row, col, player_color)
                
                state = game_manager.get_game_state(game)
                state['current_turn'] = lobby['current_turn']
                state['player_color'] = player_color
                return jsonify(state)
        
        # Одиночные игры
        else:
            if action == 'get_state':
                game = game_manager.get_or_create_game(game_type, user_id)
                return jsonify(game_manager.get_game_state(game))
            
            elif action == 'reset':
                game = game_manager.reset_game(game_type, user_id)
                return jsonify(game_manager.get_game_state(game))
            
            elif action == 'move':
                game = game_manager.get_or_create_game(game_type, user_id)
                direction = data.get('direction')
                
                if game_type in ['snake', '2048', 'flappy', 'tetris', 'pacman', 'space_invaders']:
                    game.move(direction)
                
                if game.game_over and hasattr(game, 'score'):
                    won = getattr(game, 'won', False)
                    from backend.scores.score_manager import ScoreManager
                    ScoreManager.save_score(int(user_id), nickname, game_type, game.score, won)
                    game_manager.remove_game(game_type, user_id)
                
                return jsonify(game_manager.get_game_state(game))
            
            elif action == 'direction' and game_type in ['snake', 'pacman']:
                game = game_manager.get_or_create_game(game_type, user_id)
                direction = data.get('direction')
                if direction:
                    game.change_direction(direction)
                return jsonify({'status': 'ok'})
            
            elif action == 'reveal' and game_type == 'minesweeper':
                game = game_manager.get_or_create_game(game_type, user_id)
                x = data.get('x')
                y = data.get('y')
                if x is not None and y is not None:
                    game.reveal(x, y)
                
                if game.game_over and hasattr(game, 'score'):
                    won = getattr(game, 'won', False)
                    from backend.scores.score_manager import ScoreManager
                    ScoreManager.save_score(int(user_id), nickname, game_type, game.score, won)
                    game_manager.remove_game(game_type, user_id)
                
                return jsonify(game_manager.get_game_state(game))
            
            elif action == 'toggle_flag' and game_type == 'minesweeper':
                game = game_manager.get_or_create_game(game_type, user_id)
                x = data.get('x')
                y = data.get('y')
                if x is not None and y is not None:
                    game.toggle_flag(x, y)
                return jsonify(game_manager.get_game_state(game))
            
            elif action == 'auto_reveal' and game_type == 'minesweeper':
                game = game_manager.get_or_create_game(game_type, user_id)
                x = data.get('x')
                y = data.get('y')
                if x is not None and y is not None:
                    game.auto_reveal_around(x, y)
                return jsonify(game_manager.get_game_state(game))
            
            else:
                return jsonify({'error': 'Unknown action'}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Game API Error] {e}")
        return jsonify({
            'error': str(e), 
            'map_html': '<div>Ошибка игры</div>', 
            'score': 0, 
            'game_over': True, 
            'won': False
        }), 500