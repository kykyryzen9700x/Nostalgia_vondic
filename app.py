from flask import Flask, render_template, request, redirect, session, url_for
from backend.config import config
from backend.database.db_manager import init_db
from backend.scores.score_manager import ScoreManager
from backend.database.models import (get_or_create_user_by_vondic, get_user_by_id,
                                     get_all_tickets, get_ticket, update_ticket_response,
                                     create_ticket_from_bot)
from backend.oauth.oauth_client import get_authorization_url, exchange_code_for_token, get_user_info
from botiksdk.client import PublicAPIClient
import secrets
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG
init_db()

# Регистрация blueprint для игр и рекордов (без auth_bp)
from backend.games.game_routes import game_bp
from backend.scores.score_routes import scores_bp
app.register_blueprint(game_bp)
app.register_blueprint(scores_bp)

# ---------- Декоратор для админ-доступа ----------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = get_user_by_id(session['user_id'])
        if not user or not user['is_admin']:
            return "Доступ запрещён", 403
        return f(*args, **kwargs)
    return decorated

# ---------- OAuth маршруты ----------
@app.route('/login')
def login():
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    auth_url = get_authorization_url(state)
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    error = request.args.get('error')
    if error:
        return f"Ошибка авторизации: {error}", 400

    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return "Недостаточно параметров", 400

    if state != session.pop('oauth_state', None):
        return "Неверный state (CSRF)", 400

    try:
        access_token = exchange_code_for_token(code)
        user_info = get_user_info(access_token)
    except Exception as e:
        return f"Ошибка при обмене токена: {e}", 500

    vondic_id = user_info['id']
    username = user_info.get('username', user_info.get('email', 'user'))
    email = user_info.get('email', '')
    user_id, is_admin = get_or_create_user_by_vondic(vondic_id, username, email)

    session['user_id'] = user_id
    session['username'] = username
    session['is_admin'] = is_admin
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ---------- Главная ----------
@app.route('/')
def index():
    try:
        pacman_scores = ScoreManager.get_top_scores('pacman', 5)
        snake_scores = ScoreManager.get_top_scores('snake', 5)
        minesweeper_scores = ScoreManager.get_top_scores('minesweeper', 5)
    except Exception as e:
        print(f"Error loading scores: {e}")
        pacman_scores = []
        snake_scores = []
        minesweeper_scores = []
    return render_template('index.html',
                         pacman_scores=pacman_scores,
                         snake_scores=snake_scores,
                         minesweeper_scores=minesweeper_scores)

# ---------- Админка тикетов ----------
@app.route('/admin/tickets')
@admin_required
def admin_tickets():
    tickets = get_all_tickets()
    return render_template('admin_tickets.html', tickets=tickets)

@app.route('/admin/ticket/<int:ticket_id>')
@admin_required
def admin_ticket_view(ticket_id):
    ticket = get_ticket(ticket_id)
    if not ticket:
        return "Тикет не найден", 404
    return render_template('admin_ticket.html', ticket=ticket)

@app.route('/admin/ticket/<int:ticket_id>/reply', methods=['POST'])
@admin_required
def admin_ticket_reply(ticket_id):
    ticket = get_ticket(ticket_id)
    if not ticket:
        return {'error': 'Тикет не найден'}, 404

    reply_text = request.form.get('reply', '').strip()
    if not reply_text:
        return {'error': 'Ответ не может быть пустым'}, 400

    # Сохраняем ответ в БД
    update_ticket_response(ticket_id, reply_text)

    # Отправляем ответ пользователю через бота
    if config.BOT_TOKEN and ticket['vondic_chat_id']:
        try:
            client = PublicAPIClient(base_url=config.BOT_BASE_URL)
            bot_id = config.BOT_TOKEN.split(':')[0] if ':' in config.BOT_TOKEN else ''
            client.send_message(
                bot_id=bot_id,
                bot_token=config.BOT_TOKEN,
                chat_id=ticket['vondic_chat_id'],
                text=f"📝 Ответ на обращение #{ticket_id}:\n\n{reply_text}"
            )
            return {'success': True}
        except Exception as e:
            print(f"Ошибка отправки ответа: {e}")
            return {'error': 'Не удалось отправить ответ в бот'}, 500
    else:
        return {'error': 'Не настроен бот или нет chat_id'}, 500


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    # Получаем лучшие результаты по каждой игре
    games = ['pacman', 'snake', 'minesweeper', 'flappy', '2048', 'tetris', 'space_invaders', 'checkers', 'chess']
    best_scores = {}
    for game in games:
        best = ScoreManager.get_best_score(session['user_id'], game)
        best_scores[game] = best if best else 0

    # Последние игры
    recent_scores = ScoreManager.get_user_scores(session['user_id'], limit=10)

    return render_template('profile.html',
                         user=user,
                         best_scores=best_scores,
                         recent_scores=recent_scores)

# ---------- Запуск ----------
if __name__ == '__main__':
    app.run(host='192.168.3.166', port=8080, debug=True)
