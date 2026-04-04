from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sqlite3
import hashlib
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ==================== 商品データ ====================
PRODUCTS = [
    {'id': 1,  'name': '食パン',       'price': 200, 'emoji': '🍞'},
    {'id': 2,  'name': '牛乳',         'price': 180, 'emoji': '🥛'},
    {'id': 3,  'name': 'オレンジ',     'price': 120, 'emoji': '🍊'},
    {'id': 4,  'name': 'バター',       'price': 350, 'emoji': '🧈'},
    {'id': 5,  'name': '卵（6個）',    'price': 250, 'emoji': '🥚'},
    {'id': 6,  'name': 'りんご',       'price': 150, 'emoji': '🍎'},
    {'id': 7,  'name': 'ヨーグルト',   'price': 200, 'emoji': '🫙'},
    {'id': 8,  'name': 'チーズ',       'price': 400, 'emoji': '🧀'},
    {'id': 9,  'name': 'オレンジジュース', 'price': 160, 'emoji': '🧃'},
    {'id': 10, 'name': 'クロワッサン', 'price': 180, 'emoji': '🥐'},
]

# ==================== DB初期化 ====================
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, name TEXT)''')
    # テスト用アカウントを自動作成
    test_accounts = [
        ('kingbookpay86@gmail.com',  'password123', '山田 太郎'),
        ('alice@example.com', 'alice456',    '鈴木 アリス'),
        ('bob@example.com',   'bob789',      '田中 ボブ'),
        # ↑ここに ('メールアドレス', 'パスワード', '名前') の形式で追加できます
    ]
    for email, pw, name in test_accounts:
        hashed = hashlib.sha256(pw.encode()).hexdigest()
        try:
            c.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                      (email, hashed, name))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

def check_user(email, password):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT id, name FROM users WHERE email=? AND password=?', (email, hashed))
    user = c.fetchone()
    conn.close()
    return user

def register_user(email, password, name):
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                  (email, hashed, name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# ==================== メール送信 ====================
def send_purchase_email(to_email, items, user_name):
    smtp_server   = os.getenv('SMTP_SERVER',   'smtp.gmail.com')
    smtp_port     = int(os.getenv('SMTP_PORT', 587))
    smtp_user     = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        print('[INFO] メール設定なし。スキップします。')
        return False

    total = sum(item['price'] for item in items)

    # テキスト版（シンプルに商品ごと1行）
    items_text = '\n'.join([f'・{i["emoji"]} {i["name"]}　¥{i["price"]}' for i in items])

    # HTML版（テーブルで見やすく）
    items_html = ''.join([
        f'<tr>'
        f'<td style="padding:8px 12px;border-bottom:1px solid #eee;">'
        f'{i["emoji"]} {i["name"]}</td>'
        f'<td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;font-weight:600;">'
        f'¥{i["price"]}</td>'
        f'</tr>'
        for i in items
    ])

    msg = MIMEMultipart('alternative')
    msg['Subject'] = '【ご購入ありがとうございます】購入完了のお知らせ'
    msg['From']    = smtp_user
    msg['To']      = to_email

    text_body = f"""\
{user_name} 様

この度はお買い上げいただきありがとうございます。

【ご購入商品】
{items_text}

【合計金額】
{total:,}円

またのご利用をお待ちしております。
フレッシュマーケット
"""

    html_body = f"""\
<html>
<body style="font-family:'Hiragino Kaku Gothic Pro',sans-serif;
             max-width:560px;margin:0 auto;padding:24px;background:#f9f9f6;">
  <div style="background:#ffffff;border-radius:14px;padding:36px;
              box-shadow:0 2px 12px rgba(0,0,0,0.08);">

    <p style="font-size:1.5rem;margin:0 0 4px;">🌿 フレッシュマーケット</p>
    <hr style="border:none;border-top:1px solid #eee;margin:12px 0 24px;">

    <p style="font-size:1rem;color:#1b1b1b;">
      <strong>{user_name} 様</strong>
    </p>
    <p style="color:#555;line-height:1.8;">
      この度はお買い上げいただきありがとうございます。<br>
      以下の内容でご購入が完了しました。
    </p>

    <h3 style="color:#2d6a4f;margin:24px 0 10px;font-size:0.95rem;
               letter-spacing:0.05em;">【ご購入商品】</h3>
    <table style="width:100%;border-collapse:collapse;
                  background:#f9f9f6;border-radius:8px;overflow:hidden;">
      {items_html}
    </table>

    <div style="text-align:right;margin-top:16px;padding:12px 12px 0;
                border-top:2px solid #2d6a4f;">
      <span style="color:#555;font-size:0.9rem;">合計金額</span>
      <span style="font-size:1.4rem;font-weight:700;color:#2d6a4f;
                   margin-left:16px;">¥{total:,}</span>
    </div>

    <p style="color:#888;font-size:0.82rem;margin-top:32px;
              border-top:1px solid #eee;padding-top:16px;">
      またのご利用をお待ちしております。<br>
      フレッシュマーケット
    </p>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html',  'utf-8'))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f'[INFO] メール送信成功 → {to_email}')
        return True
    except Exception as e:
        print(f'[ERROR] メール送信失敗: {e}')
        return False

# ==================== ルーティング ====================
@app.route('/')
def index():
    return redirect(url_for('products') if 'user_email' in session else url_for('login'))

# --- ログイン ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('products'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = check_user(email, password)
        if user:
            session['user_email'] = email
            session['user_name']  = user[1] if user[1] else email
            session['cart'] = []
            return redirect(url_for('products'))
        flash('メールアドレスまたはパスワードが間違っています', 'error')
    return render_template('login.html')

# --- 新規登録 ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name     = request.form.get('name', '').strip()
        if register_user(email, password, name):
            flash('登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('login'))
        flash('このメールアドレスはすでに登録済みです', 'error')
    return render_template('register.html')

# --- ログアウト ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 商品一覧 ---
@app.route('/products')
def products():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    return render_template('products.html', products=PRODUCTS, cart=cart)

# --- カートに追加（Ajax） ---
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Not found'}), 404
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(cart), 'product_name': product['name']})

# --- カートから削除（Ajax） ---
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    cart = session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(cart)})

# --- 会計確認 ---
@app.route('/checkout')
def checkout():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('products'))
    cart_items = []
    seen = {}
    for pid in cart:
        product = next((p for p in PRODUCTS if p['id'] == pid), None)
        if product:
            if pid in seen:
                seen[pid]['qty'] += 1
            else:
                item = dict(product)
                item['qty'] = 1
                seen[pid] = item
                cart_items.append(item)
    total = sum(i['price'] * i['qty'] for i in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

# --- 購入確定 ---
@app.route('/purchase', methods=['POST'])
def purchase():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('products'))

    cart_items = []
    seen = {}
    for pid in cart:
        product = next((p for p in PRODUCTS if p['id'] == pid), None)
        if product:
            if pid in seen:
                seen[pid]['qty'] += 1
            else:
                item = dict(product)
                item['qty'] = 1
                seen[pid] = item
                cart_items.append(item)

    user_email = session['user_email']
    user_name  = session.get('user_name', user_email)

    # メール用にフラット展開
    flat_items = []
    for item in cart_items:
        for _ in range(item['qty']):
            flat_items.append({
                'name': item['name'],
                'price': item['price'],
                'emoji': item['emoji']
            })

    email_sent = send_purchase_email(user_email, flat_items, user_name)

    session['cart'] = []
    session.modified = True

    total = sum(i['price'] * i['qty'] for i in cart_items)
    return render_template('complete.html',
                           cart_items=cart_items,
                           total=total,
                           email_sent=email_sent,
                           user_email=user_email,
                           user_name=user_name)

# ==================== 起動 ====================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
