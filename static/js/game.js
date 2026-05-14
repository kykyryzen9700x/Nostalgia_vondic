let gameType = window.GAME_TYPE || 'snake';
let gameInterval = null;
let flagMode = false;
let pressTimer = null;

// Функция для проверки ошибки авторизации
function checkAuthError(response) {
    if (response.status === 401) {
        response.json().then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                window.location.href = '/login';
            }
        }).catch(() => {
            window.location.href = '/login';
        });
        return true;
    }
    return false;
}

function updateGameUI(data) {
    const board = document.getElementById('game-board');
    if (board) board.innerHTML = data.map_html;
    const scoreSpan = document.getElementById('score');
    if (scoreSpan) scoreSpan.textContent = data.score;
    
    if (data.game_over) {
        if (gameInterval) {
            clearInterval(gameInterval);
            gameInterval = null;
        }
        setTimeout(() => {
            if (data.won) alert('🏆 ПОБЕДА!');
            else alert('💀 ИГРА ОКОНЧЕНА');
        }, 50);
    }
}

function getGameState() {
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'get_state'})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) updateGameUI(data);
    })
    .catch(error => console.error('Get state error:', error));
}

function sendMove(direction) {
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'move', direction: direction})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) updateGameUI(data);
    })
    .catch(error => console.error('Move error:', error));
}

function sendDirection(direction) {
    console.log('Sending direction:', direction);
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'direction', direction: direction})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) console.log('Direction response:', data);
    })
    .catch(error => console.error('Direction error:', error));
}

function resetGame() {
    if (gameInterval) {
        clearInterval(gameInterval);
        gameInterval = null;
    }
    
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'reset'})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (!data) return;
        updateGameUI(data);
        // Запускаем интервал для игр с автоматическим движением
        if (gameType === 'snake') {
            startAutoMoveInterval(150);
        } else if (gameType === 'pacman') {
            startAutoMoveInterval(130);
        } else if (gameType === 'flappy') {
            startFlappyInterval();
        } else if (gameType === 'tetris') {
            startTetrisInterval();
        } else if (gameType === 'space_invaders') {
            startSpaceInvadersInterval();
        }
    })
    .catch(error => console.error('Reset error:', error));
}

function startAutoMoveInterval(speed) {
    if (gameInterval) clearInterval(gameInterval);
    
    console.log('Starting auto-move interval for:', gameType, 'speed:', speed);
    
    gameInterval = setInterval(() => {
        fetch(`/api/game/${gameType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'move'})
        })
        .then(response => {
            if (checkAuthError(response)) return;
            return response.json();
        })
        .then(data => {
            if (data) {
                updateGameUI(data);
                if (data.game_over && gameInterval) {
                    clearInterval(gameInterval);
                    gameInterval = null;
                }
            }
        })
        .catch(error => console.error('Auto-move error:', error));
    }, speed);
}

function startFlappyInterval() {
    if (gameInterval) clearInterval(gameInterval);
    
    gameInterval = setInterval(() => {
        fetch(`/api/game/${gameType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'move'})
        })
        .then(response => {
            if (checkAuthError(response)) return;
            return response.json();
        })
        .then(data => {
            if (data) {
                updateGameUI(data);
                if (data.game_over && gameInterval) {
                    clearInterval(gameInterval);
                    gameInterval = null;
                }
            }
        })
        .catch(error => console.error('Flappy move error:', error));
    }, 200);
}

function startTetrisInterval() {
    if (gameInterval) clearInterval(gameInterval);
    
    gameInterval = setInterval(() => {
        fetch(`/api/game/${gameType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'move'})
        })
        .then(response => {
            if (checkAuthError(response)) return;
            return response.json();
        })
        .then(data => {
            if (data) {
                updateGameUI(data);
                if (data.game_over && gameInterval) {
                    clearInterval(gameInterval);
                    gameInterval = null;
                }
            }
        })
        .catch(error => console.error('Tetris move error:', error));
    }, 50);
}

function startSpaceInvadersInterval() {
    if (gameInterval) clearInterval(gameInterval);
    
    console.log('Starting Space Invaders game loop');
    
    gameInterval = setInterval(() => {
        fetch(`/api/game/${gameType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: 'move'})
        })
        .then(response => {
            if (checkAuthError(response)) return;
            return response.json();
        })
        .then(data => {
            if (data) {
                updateGameUI(data);
                if (data.game_over && gameInterval) {
                    clearInterval(gameInterval);
                    gameInterval = null;
                }
            }
        })
        .catch(error => console.error('Space Invaders loop error:', error));
    }, 50);
}

// Кнопки управления
document.querySelectorAll('.control-btn[data-direction], .snake-control-btn[data-direction]').forEach(btn => {
    btn.addEventListener('click', () => {
        const direction = btn.dataset.direction;
        console.log('Button clicked:', direction, 'Game type:', gameType);
        
        if (gameType === 'pacman' || gameType === 'snake') {
            sendDirection(direction);
        } else if (gameType === 'flappy' && direction === 'up') {
            sendMove(direction);
        } else if (gameType === '2048') {
            sendMove(direction);
        } else if (gameType === 'tetris') {
            sendMove(direction);
        } else if (gameType === 'space_invaders' && (direction === 'left' || direction === 'right')) {
            sendMove(direction);
        }
    });
});

// Управление клавиатурой
document.addEventListener('keydown', function(e) {
    let direction = null;
    
    if (e.code === 'Space') {
        e.preventDefault();
        if (gameType === 'tetris') {
            sendMove('space');
        } else if (gameType === 'flappy') {
            sendMove('up');
        } else if (gameType === 'space_invaders') {
            sendMove('space');
        }
        return;
    }
    
    switch(e.key) {
        case 'ArrowUp': direction = 'up'; break;
        case 'ArrowDown': direction = 'down'; break;
        case 'ArrowLeft': direction = 'left'; break;
        case 'ArrowRight': direction = 'right'; break;
        case 'w': case 'W': direction = 'up'; break;
        case 's': case 'S': direction = 'down'; break;
        case 'a': case 'A': direction = 'left'; break;
        case 'd': case 'D': direction = 'right'; break;
        default: return;
    }
    
    e.preventDefault();
    
    if (gameType === 'pacman' || gameType === 'snake') {
        sendDirection(direction);
    } else if (gameType === 'flappy' && direction === 'up') {
        sendMove(direction);
    } else if (gameType === '2048') {
        sendMove(direction);
    } else if (gameType === 'tetris') {
        sendMove(direction);
    } else if (gameType === 'space_invaders' && (direction === 'left' || direction === 'right')) {
        sendMove(direction);
    }
});

// ==================== ДЛЯ САПЁРА ====================
function toggleFlagMode() {
    flagMode = !flagMode;
    const flagText = document.getElementById('flagModeText');
    if (flagText) flagText.textContent = flagMode ? 'ВКЛ' : 'ВЫКЛ';
}

function revealCell(x, y) {
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'reveal', x: x, y: y})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) updateGameUI(data);
    })
    .catch(error => console.error('Reveal error:', error));
}

function toggleFlag(x, y) {
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'toggle_flag', x: x, y: y})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) updateGameUI(data);
    })
    .catch(error => console.error('Toggle flag error:', error));
}

function autoRevealAround(x, y) {
    fetch(`/api/game/${gameType}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({action: 'auto_reveal', x: x, y: y})
    })
    .then(response => {
        if (checkAuthError(response)) return;
        return response.json();
    })
    .then(data => {
        if (data) updateGameUI(data);
    })
    .catch(error => console.error('Auto reveal error:', error));
}

if (gameType === 'minesweeper') {
    document.addEventListener('click', function(e) {
        let cell = e.target.closest('.game-cell');
        if (!cell) return;
        
        let x = parseInt(cell.dataset.x);
        let y = parseInt(cell.dataset.y);
        
        if (e.button === 0) {
            if (flagMode) {
                toggleFlag(x, y);
            } else {
                revealCell(x, y);
            }
        }
    });
    
    document.addEventListener('contextmenu', function(e) {
        let cell = e.target.closest('.game-cell');
        if (cell) {
            e.preventDefault();
            let x = parseInt(cell.dataset.x);
            let y = parseInt(cell.dataset.y);
            toggleFlag(x, y);
        }
    });
    
    document.addEventListener('mousedown', function(e) {
        let cell = e.target.closest('.game-cell');
        if (cell && e.button === 0) {
            pressTimer = setTimeout(() => {
                let x = parseInt(cell.dataset.x);
                let y = parseInt(cell.dataset.y);
                toggleFlag(x, y);
                pressTimer = null;
            }, 500);
        }
    });
    
    document.addEventListener('mouseup', function(e) {
        if (pressTimer) {
            clearTimeout(pressTimer);
            pressTimer = null;
        }
    });
    
    document.addEventListener('click', function(e) {
        let cell = e.target.closest('.game-cell');
        if (!cell) return;
        
        let x = parseInt(cell.dataset.x);
        let y = parseInt(cell.dataset.y);
        
        if (cell.classList && cell.classList.contains('revealed') && !cell.classList.contains('mine')) {
            autoRevealAround(x, y);
        }
    });
}

// Запуск игры после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, game type:', gameType);
    resetGame();
    
    if (gameType === 'snake') {
        startAutoMoveInterval(150);
    } else if (gameType === 'pacman') {
        startAutoMoveInterval(130);
    } else if (gameType === 'flappy') {
        startFlappyInterval();
    } else if (gameType === 'tetris') {
        startTetrisInterval();
    } else if (gameType === 'space_invaders') {
        startSpaceInvadersInterval();
    }
});