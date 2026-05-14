from flask import Blueprint, jsonify, request, session
from backend.scores.score_manager import ScoreManager


scores_bp = Blueprint('scores', __name__)


@scores_bp.route('/api/scores/top')
def get_top_scores():
    #api для получения топ рекордов
    game_type = request.args.get('game_type')
    limit = request.args.get('limit', 10, type=int)
    scores = ScoreManager.get_top_scores(game_type, limit)
    return jsonify({
        'scores': [dict(score) for score in scores],
        'total': len(scores)
    })


@scores_bp.route('/api/scores/my')
def get_my_scores():
    #api для получения рекордов конкретного игрока сейчас
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    game_type = request.args.get('game_type')
    limit = request.args.get('limit', 20, type=int)
    scores = ScoreManager.get_user_scores(session['user_id'], limit)
    return jsonify({
        'scores': [dict(score) for score in scores],
        'total': len(scores)
    })


@scores_bp.route('/api/scores/best/<game_type>')
def get_best_score(game_type):
    #api для получения лучшего результата пользователя в игре
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    best = ScoreManager.get_best_score(session['user_id'], game_type)
    return jsonify({
        'game_type': game_type,
        'best_score': best
    })