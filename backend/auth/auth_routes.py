from flask import Blueprint, render_template, request, redirect, session
from backend.auth.user_manager import UserManager
from backend.auth.security import validate_email, validate_password
from backend.config import config


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not validate_email(email):
            return render_template('register.html', error='Некорректный email!')
        if not validate_password(password, config.MIN_PASSWORD_LENGTH):
            return render_template('register.html', 
                                 error=f'Пароль должен быть минимум {config.MIN_PASSWORD_LENGTH} символов!')
        success, user_id, error = UserManager.register(email, password)
        if success:
            session['user_id'] = user_id
            user_info = UserManager.get_user_info(user_id)
            session['nickname'] = user_info['nickname'] if user_info and user_info['nickname'] else None
            if not session['nickname'] or session['nickname'].startswith('user_'):
                return redirect('/set_nickname')
            return redirect('/')
        else:
            return render_template('register.html', error=error)
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = UserManager.authenticate(email, password)
        if user:
            session['user_id'] = user['id']
            session['nickname'] = user['nickname']
            if not user['nickname'] or user['nickname'].startswith('user_'):
                return redirect('/set_nickname')
            return redirect('/')
        else:
            return render_template('login.html', error='Неверный email или пароль!')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    error = None
    success = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_nickname':
            new_nickname = request.form.get('new_nickname', '').strip()
            if not new_nickname:
                error = 'Никнейм не может быть пустым!'
            elif len(new_nickname) < config.MIN_NICKNAME_LENGTH:
                error = f'Никнейм должен быть минимум {config.MIN_NICKNAME_LENGTH} символа!'
            else:
                success, error = UserManager.change_nickname(session['user_id'], new_nickname)
                if success:
                    session['nickname'] = new_nickname
        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            if new_password != confirm_password:
                error = 'Пароли не совпадают!'
            elif len(new_password) < config.MIN_PASSWORD_LENGTH:
                error = f'Новый пароль должен быть минимум {config.MIN_PASSWORD_LENGTH} символов!'
            else:
                success, error = UserManager.change_password(session['user_id'], old_password, new_password)
    user_info = UserManager.get_user_info(session['user_id'])
    from backend.scores.score_manager import ScoreManager
    user_scores = ScoreManager.get_user_scores(session['user_id'])
    return render_template('profile.html', 
                         nickname=session['nickname'],
                         email=user_info['email'] if user_info else '',
                         user_scores=user_scores,
                         error=error,
                         success=success)