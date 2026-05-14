from backend.database.db_manager import get_db


def create_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vondic_user_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nickname TEXT NOT NULL,
                game_type TEXT NOT NULL,
                score INTEGER NOT NULL,
                won BOOLEAN DEFAULT 0,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,                -- local user id (если авторизован)
                vondic_chat_id TEXT NOT NULL,   -- chat_id в Vondic
                message TEXT NOT NULL,
                admin_response TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                replied_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_game ON scores(game_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_score ON scores(score DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_user ON scores(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_chat ON support_tickets(vondic_chat_id)')
        cursor.execute("SELECT id FROM users WHERE is_admin = 1 LIMIT 1")
        if not cursor.fetchone():
            print("[DB] No admin found. After OAuth login, set is_admin=1 manually.")
        print("[DB] Tables created successfully")


def get_or_create_user_by_vondic(vondic_id, username, email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, is_admin FROM users WHERE vondic_user_id = ?', (vondic_id,))
        row = cursor.fetchone()
        if row:
            return row['id'], row['is_admin']
        cursor.execute('''
            INSERT INTO users (vondic_user_id, username, email, is_admin)
            VALUES (?, ?, ?, 0)
        ''', (vondic_id, username, email))
        return cursor.lastrowid, 0

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, vondic_user_id, username, email, is_admin FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def get_user_by_vondic_id(vondic_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, is_admin FROM users WHERE vondic_user_id = ?', (vondic_id,))
        return cursor.fetchone()


def create_ticket_from_bot(vondic_chat_id, message, local_user_id=None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO support_tickets (user_id, vondic_chat_id, message, status)
            VALUES (?, ?, ?, 'open')
        ''', (local_user_id, vondic_chat_id, message))
        return cursor.lastrowid

def get_all_tickets(limit=100):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, vondic_chat_id, message, admin_response, status,
                   created_at, replied_at
            FROM support_tickets
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

def get_ticket(ticket_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM support_tickets WHERE id = ?', (ticket_id,))
        return cursor.fetchone()

def update_ticket_response(ticket_id, admin_response):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE support_tickets
            SET admin_response = ?, status = 'answered', replied_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (admin_response, ticket_id))
        return cursor.rowcount > 0
