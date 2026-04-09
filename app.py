from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import subprocess
import ctypes
import secrets
import hashlib

app = Flask(__name__)
CORS(app)

# Шлях до файлу з замовленнями
ORDERS_FILE = 'orders.json'
USERS_FILE = 'users.json'

# Завантаження C++ бібліотеки
try:
    # Спроба завантажити скомпільовану C++ бібліотеку
    if os.name == 'nt':  # Windows
        cpp_lib = ctypes.CDLL('./order_processor.dll')
    else:  # Linux/Mac
        cpp_lib = ctypes.CDLL('./order_processor.so')
    
    # Налаштування функцій з C++
    cpp_lib.calculate_price.argtypes = [ctypes.c_char_p, ctypes.c_int]
    cpp_lib.calculate_price.restype = ctypes.c_float
    cpp_lib_available = True
except:
    cpp_lib_available = False
    print("C++ бібліотека не знайдена. Використовується Python обробка.")

def load_orders():
    """Завантаження замовлень з файлу"""
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_orders(orders):
    """Збереження замовлень у файл"""
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def load_users():
    """Завантаження користувачів з файлу"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_users(users):
    """Збереження користувачів у файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Хешування пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Генерація токена для сесії"""
    return secrets.token_hex(32)

def calculate_price_python(service_type, description_length):
    """Python альтернатива для розрахунку ціни"""
    base_prices = {
        'website': 2000,
        'notes': 100,
        'programming': 150,
        'coursework': 500,
        'other': 200
    }
    
    base_price = base_prices.get(service_type, 200)
    complexity_multiplier = 1 + (description_length / 1000) * 0.5
    
    return base_price * complexity_multiplier

def calculate_price(service_type, description_length):
    """Розрахунок ціни з використанням C++ або Python"""
    if cpp_lib_available:
        try:
            service_bytes = service_type.encode('utf-8')
            price = cpp_lib.calculate_price(service_bytes, description_length)
            return float(price)
        except:
            pass
    return calculate_price_python(service_type, description_length)

@app.route('/')
def index():
    """Головна сторінка"""
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Реєстрація нового користувача"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email та пароль є обов\'язковими'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Пароль має бути не менше 6 символів'}), 400
        
        # Перевірка чи існує користувач
        users = load_users()
        if any(user['email'] == email for user in users):
            return jsonify({'message': 'Користувач з таким email вже існує'}), 400
        
        # Створення нового користувача
        user = {
            'id': len(users) + 1,
            'email': email,
            'password_hash': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        users.append(user)
        save_users(users)
        
        # Генерація токена
        token = generate_token()
        
        # Повернення даних користувача без пароля
        user_response = {
            'id': user['id'],
            'email': user['email'],
            'created_at': user['created_at']
        }
        
        return jsonify({
            'message': 'Реєстрація успішна',
            'user': user_response,
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Вхід користувача"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email та пароль є обов\'язковими'}), 400
        
        # Пошук користувача
        users = load_users()
        user = next((u for u in users if u['email'] == email), None)
        
        if not user:
            return jsonify({'message': 'Невірний email або пароль'}), 401
        
        # Перевірка пароля
        if user['password_hash'] != hash_password(password):
            return jsonify({'message': 'Невірний email або пароль'}), 401
        
        # Генерація токена
        token = generate_token()
        
        # Повернення даних користувача без пароля
        user_response = {
            'id': user['id'],
            'email': user['email'],
            'created_at': user['created_at']
        }
        
        return jsonify({
            'message': 'Вхід успішний',
            'user': user_response,
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/order', methods=['POST'])
def create_order():
    """Обробка замовлення"""
    try:
        data = request.json
        
        # Валідація даних
        required_fields = ['name', 'email', 'service', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Поле {field} є обов\'язковим'}), 400
        
        # Розрахунок орієнтовної ціни
        description_length = len(data.get('description', ''))
        estimated_price = calculate_price(data['service'], description_length)
        
        # Створення замовлення
        order = {
            'id': len(load_orders()) + 1,
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'service': data['service'],
            'description': data['description'],
            'deadline': data.get('deadline', ''),
            'budget': data.get('budget', 0),
            'estimated_price': round(estimated_price, 2),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        # Збереження замовлення
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        
        return jsonify({
            'message': 'Замовлення успішно створено',
            'order_id': order['id'],
            'estimated_price': order['estimated_price']
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Отримання списку всіх замовлень"""
    try:
        orders = load_orders()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Отримання замовлення за ID"""
    try:
        orders = load_orders()
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if order:
            return jsonify(order), 200
        else:
            return jsonify({'message': 'Замовлення не знайдено'}), 404
            
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Оновлення статусу замовлення"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Статус не вказано'}), 400
        
        orders = load_orders()
        order = next((o for o in orders if o['id'] == order_id), None)
        
        if order:
            order['status'] = new_status
            order['updated_at'] = datetime.now().isoformat()
            save_orders(orders)
            return jsonify({'message': 'Статус оновлено'}), 200
        else:
            return jsonify({'message': 'Замовлення не знайдено'}), 404
            
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Отримання статистики замовлень"""
    try:
        orders = load_orders()
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o['status'] == 'pending'])
        completed_orders = len([o for o in orders if o['status'] == 'completed'])
        
        service_stats = {}
        for order in orders:
            service = order['service']
            service_stats[service] = service_stats.get(service, 0) + 1
        
        return jsonify({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'service_stats': service_stats
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Помилка: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
