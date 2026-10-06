from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "profile-card-secret-key"
DB_PATH = Path(__file__).parent / "profiles.db"

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        bio TEXT NOT NULL,
        skills TEXT NOT NULL,
        github TEXT,
        linkedin TEXT,
        instagram TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()
    db.close()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        bio = request.form.get('bio','').strip()
        skills = request.form.get('skills','').strip()
        github = request.form.get('github','').strip()
        linkedin = request.form.get('linkedin','').strip()
        instagram = request.form.get('instagram','').strip()
        if not name or not bio or not skills:
            flash('Name, Bio and Skills are required.', 'error')
            return render_template('index.html')
        db = get_db()
        cur = db.execute('''INSERT INTO profiles
            (name,bio,skills,github,linkedin,instagram)
            VALUES (?,?,?,?,?,?)''', (name,bio,skills,github,linkedin,instagram))
        profile_id = cur.lastrowid
        db.commit()
        profile = db.execute('SELECT * FROM profiles WHERE id=?', (profile_id,)).fetchone()
        db.close()
        return render_template('profile.html', profile=profile)
    return render_template('index.html')

@app.route('/profiles')
def profiles():
    db = get_db()
    rows = db.execute('SELECT * FROM profiles ORDER BY id DESC').fetchall()
    db.close()
    return render_template('profiles.html', profiles=rows)

@app.route('/profile/<int:profile_id>')
def profile(profile_id):
    db = get_db()
    row = db.execute('SELECT * FROM profiles WHERE id=?', (profile_id,)).fetchone()
    db.close()
    if row is None:
        flash('Profile not found.', 'error')
        return redirect(url_for('profiles'))
    return render_template('profile.html', profile=row)

@app.route('/delete/<int:profile_id>', methods=['POST'])
def delete_profile(profile_id):
    db = get_db()
    db.execute('DELETE FROM profiles WHERE id=?', (profile_id,))
    db.commit()
    db.close()
    flash('Profile deleted successfully.', 'success')
    return redirect(url_for('profiles'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
