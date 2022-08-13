import sqlite3


def check_tables(db):
    try:
        cur = db.cursor()
        cursor = db.cursor()
        cur.execute("SELECT * FROM users")
        cursor.execute("SELECT * FROM words")
    except sqlite3.DataError:
        create_tables(db)

    

def create_tables(db):
    print("Creating tables: ", end='')

    cur = db.cursor()
    cursor = db.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, sending BOOL, send_period INTEGER NOT NULL)")
    cursor.execute("CREATE TABLE words (id INTEGER PRIMARY KEY AUTOINCREMENT, word varchar(64) NOT NULL, translated_word varchar(64) NOT NULL, user_id INTEGER NOT NULL REFERENCES users (id), sent BOOL)")
    db.commit()

    print("done")


def create_user(db, id):
    """
    Function that add new user and if user has been add then return False
    """
    try:
        cur = db.cursor()
        cur.execute(f"INSERT INTO users (id) VALUES ({id})")
        db.commit()

    except sqlite3.IntegrityError:
        return False

    return True


def create_word(db, word, tr_word, user_id):
    """
    Function that add new user`s word with user`s Telegram ID
    """
    cur = db.cursor()
    cur.execute(f"INSERT INTO words (word, translated_word, user_id, sent) VALUES ('{word}', '{tr_word}', {user_id}, {0})")
    db.commit()
        

def delete_word(db, in_word):
    """
    Function that remove user`s word
    """
    cur = db.cursor()
    cur.execute(f"DELETE FROM words WHERE word = '{in_word}' OR translated_word = '{in_word}'")
    db.commit()


def get_words(db, id):
    """
    Function returns list of user`s words
    """
    cur = db.cursor()
    words_list = []
    for row in cur.execute(f"SELECT word, translated_word FROM words WHERE user_id = {id}"):
        words_list.append(row)
    return words_list


def count_words_to_send(db, id):
    """
    Function returns count of words wich not sent
    """
    cur = db.cursor()
    count = 0
    for row in cur.execute(f"SELECT id FROM words WHERE user_id = {id} AND sent=0"):
        count += 1
    return count


def find_word(db, id, in_word):
    """
    Function find user`s word
    """
    cur = db.cursor()
    return cur.execute(f"SELECT word FROM words WHERE user_id = {id} AND word = '{in_word}'")


def get_word_to_send(db, period):
    """
    Function returns user`s word wich not sent
    """
    cur = db.cursor()
    cursor = cur.execute(f"SELECT word, translated_word, user_id FROM words WHERE sent=0 AND user_id=(SELECT id FROM users WHERE sending=1 AND send_period={period}) LIMIT 1;")
    return cursor.fetchall()


def get_words_to_send(db, period):
    """
    Function returns a list of words that should be sent after the end of the period
    """
    cur = db.cursor()
    cursor = db.cursor()
    words_list = []
    users = cur.execute(f"SELECT id FROM users WHERE sending=1 AND send_period = {period}")
    for user in users:
        word = tuple(cursor.execute(f"SELECT word, translated_word, user_id FROM words WHERE sent=0 AND user_id={user[0]} LIMIT 1"))
        if not word:
            continue
        words_list.append(word[0])
    return words_list


def word_sent(db, id, word):
    """
    Function that mark words with sent
    """
    cur = db.cursor()
    cur.execute(f"UPDATE words SET sent=true WHERE user_id={id} AND word='{word}'")
    db.commit()


def insert_notifications_settings(db, switch: bool, period, user_id):
    """
    Function that on or off notifications and add sending period
    """
    cur = db.cursor()
    cur.execute(f"UPDATE users SET sending={switch}, send_period={60*period} WHERE id={user_id}")
    db.commit()


def update_words_status(db, period):
    """
    Function that mark words which should be sent with a period with not sent
    """
    cur = db.cursor()
    cur.execute(f"UPDATE words SET sent=0 WHERE user_id=(SELECT id FROM users WHERE sending=1 AND send_period={period})")
    db.commit()


def update_user_words_status(db, id):
    """
    Function that mark words user`s with not sent
    """
    cur = db.cursor()
    cur.execute(f"UPDATE words SET sent=0 WHERE user_id={id}")
    db.commit()