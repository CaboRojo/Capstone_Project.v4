from functools import wraps
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
import requests
import bcrypt
from datetime import datetime, timedelta
import re
import jwt
import os

import oracledb

un = 'APIUSER'  # Your Oracle Database username
pw = 'AlexisSanchez1998'  # Your Oracle Database password
# Your Oracle Database connection string
cs = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd51c296542b64f_projectdb22023_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'

DATABASE_API_URL = "https://gd51c296542b64f-projectdb22023.adb.eu-madrid-1.oraclecloudapps.com/ords/"

def get_db_connection():
    return oracledb.connect(user=un, password=pw, dsn=cs)

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Replace 'your_api_key' with your actual AlphaVantage API key.
ALPHA_VANTAGE_API_KEY = "your_api_key"
DATABASE_API_URL = "https://example.com/api"

# Fetch the secret key for JWT from the environment, or use a fallback for development only.
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key_for_development')

def get_user_id_from_token(token):
    try:
        # Decode the token
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        # Extract and return the user ID
        return decoded_token.get("user_id")
    except jwt.ExpiredSignatureError:
        # Handle the case where the token has expired
        abort(401, 'Token has expired.')
    except jwt.InvalidTokenError:
        # Handle the case where the token is invalid
        abort(401, 'Invalid token.')

class AlphaVantageAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query?"

    def make_request(self, params):
        params['apikey'] = self.api_key  # Ensure API key is included in all requests
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Request exception: %s", e)
            return None

    def get_stock_final_price(self, symbol):
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact'
        }
        data = self.make_request(params)
        if data and 'Time Series (Daily)' in data:
            latest_date = max(data['Time Series (Daily)'].keys())
            return float(data['Time Series (Daily)'][latest_date]["4. close"])
        return None

    def get_historical_stock_prices(self, symbol):
        """Fetch historical stock prices for the last year."""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full'
        }
        data = self.make_request(params)
        if data and 'Time Series (Daily)' in data:
            one_year_ago = datetime.now() - timedelta(days=365)
            one_year_ago_str = one_year_ago.strftime('%Y-%m-%d')
            
            historical_prices = {date: info["4. close"] for date, info in data['Time Series (Daily)'].items() if date >= one_year_ago_str}
            return historical_prices
        return None


alpha_vantage_api = AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def is_password_valid(password):
    return len(password) >= 8 and re.search("[a-z]", password) and re.search("[A-Z]", password) and re.search("[0-9]", password) and re.search("[!@#$%^&*(),.?\":{}|<>]", password)

def register_user(username, email, password):
    if not is_password_valid(password):
        return False, "Password does not meet the security criteria.", None
    password_hash = hash_password(password)
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "account_creation_date": datetime.utcnow().isoformat(),
    }
    try:
        response = requests.post(f"{DATABASE_API_URL}/users/register", json=user_data, timeout=10)
        response.raise_for_status()
        return True, "User registered successfully.", response.json().get('user_id')
    except requests.exceptions.HTTPError as errh:
        if errh.response.status_code == 409:  # Conflict
            return False, "Username or email already exists.", None
        return False, "Error registering user: HTTPError.", None
    except requests.exceptions.ConnectionError:
        return False, "Error registering user: ConnectionError.", None
    except requests.exceptions.Timeout:
        return False, "Error registering user: Timeout.", None
    except requests.exceptions.RequestException:
        return False, "Error registering user: RequestException.", None

@app.route('/api/register', methods=['POST'])
def api_register_user():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']

    # Validate password
    if not is_password_valid(password):
        return jsonify({"error": "Password does not meet the security criteria."}), 400

    password_hash = hash_password(password)
    account_creation_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Open a new database connection
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO USERS (USERNAME, PASSWORDHASH, ACCOUNTCREATIONDATE, EMAIL) 
                         VALUES (:username, :password_hash, TO_TIMESTAMP(:account_creation_date, 'YYYY-MM-DD HH24:MI:SS'), :email)"""
                cursor.execute(sql, {'username': username, 'password_hash': password_hash, 'account_creation_date': account_creation_date, 'email': email})
                connection.commit()
        return jsonify({"message": "User registered successfully."}), 201
    except oracledb.DatabaseError as e:
        logging.error(f"Database error during registration: {e}")
        return jsonify({"error": "Error registering user, possibly a duplicate username."}), 500


def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            abort(401, 'A valid token is missing')
        
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            return f(*args, **kwargs, user_id=data['user_id'])
        except Exception:
            abort(401, 'Token is invalid or expired')
    return decorated

@app.route('/api/stock_selection', methods=['POST'])
def handle_stock_selection():
    data = request.json
    selected_stocks = data.get('selected_stocks', [])
    # Validate the number of selected stocks
    if len(selected_stocks) > 2:
        return jsonify({"error": "Please select no more than 2 stocks."}), 400
    total_investment = 0
    stock_prices = {}
    # Calculate the total investment required
    for stock in selected_stocks:
        symbol = stock.get('symbol')
        quantity = stock.get('quantity', 0)
        closing_price = alpha_vantage_api.get_stock_final_price(symbol)
        if closing_price is None:
            return jsonify({"error": f"Failed to retrieve price for {symbol}."}), 400
        stock_prices[symbol] = closing_price
        total_investment += closing_price * quantity
    # Send the total investment amount back to the frontend for confirmation
    return jsonify({"total_investment": total_investment, "stock_prices": stock_prices}), 200

@app.route('/api/confirm_selection', methods=['POST'])
@token_required
def confirm_selection(user_id):
    data = request.json
    selected_stocks = data.get('selected_stocks', [])
    confirmation = data.get('confirmation', False)

    if not confirmation:
        return jsonify({"error": "Stock selection not confirmed. Please adjust your selection."}), 400
    
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                portfolio_id = create_portfolio(cursor, user_id)
                for stock in selected_stocks:
                    symbol = stock['symbol']
                    quantity = stock['quantity']
                    transaction_price = alpha_vantage_api.get_stock_final_price(symbol)
                    if transaction_price:
                        create_transaction(cursor, portfolio_id, symbol, quantity, transaction_price)
                    else:
                        return jsonify({"error": f"Failed to create transaction for {symbol}."}), 500
                connection.commit()
        return jsonify({"message": "Portfolio and stock selections confirmed and recorded."}), 200
    except Exception as e:
        logging.error(f"Error confirming selection: {e}")
        return jsonify({"error": "Failed to confirm selection."}), 500


def create_portfolio(cursor, user_id):
    # Adapted to use uppercase for SQL query
    cursor.execute("SELECT PORTFOLIOID FROM PORTFOLIOS WHERE USERID = :1", [user_id])
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(
            "INSERT INTO PORTFOLIOS (USERID, TOTALPORTFOLIOVALUE, TOTALROI) VALUES (:1, 0, 0) RETURNING PORTFOLIOID INTO :2",
            [user_id, cursor.var(int)])
        return cursor.var(int).getvalue()[0]  # Fetch the returned portfolio_id


def create_transaction(cursor, portfolio_id, symbol, quantity, transaction_price):
    current_total_value = quantity * transaction_price
    # Adapted to use uppercase for SQL query
    cursor.execute(
        """INSERT INTO TRANSACTIONS 
           (PORTFOLIOID, SYMBOL, QUANTITY, TRANSACTIONPRICE, CURRENTTOTALVALUE, TRANSACTIONDATE, TRANSACTIONTYPE) 
           VALUES (:1, :2, :3, :4, :5, CURRENT_TIMESTAMP, 'buy')""",
        [portfolio_id, symbol, quantity, transaction_price, current_total_value])

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    username = data['username']
    password = data['password']

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Updated SQL query to match case sensitivity of the database schema
                sql = "SELECT USERID, PASSWORDHASH FROM USERS WHERE USERNAME = :1"
                cursor.execute(sql, [username])
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                    token = jwt.encode({
                        'user_id': user[0],
                        'exp': datetime.utcnow() + timedelta(hours=24)
                    }, JWT_SECRET_KEY, algorithm='HS256').decode('utf-8')

                    return jsonify({'token': token}), 200
                else:
                    return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/portfolio/<user_id>', methods=['GET'])
@token_required
def get_user_portfolio(user_id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT TOTALPORTFOLIOVALUE, TOTALROI FROM PORTFOLIOS WHERE USERID = :user_id"
                cursor.execute(sql, {"user_id": user_id})  # Use named placeholders for clarity
                portfolio_data = cursor.fetchone()

                if portfolio_data:
                    return jsonify({
                        "total_portfolio_value": portfolio_data[0],
                        "roi": portfolio_data[1]
                    }), 200
                else:
                    return jsonify({"error": "Portfolio data not found."}), 404
    except Exception as e:
        logging.error(f"Error fetching portfolio data: {e}")
        return jsonify({"error": "Unable to fetch portfolio data."}), 500


@app.route('/api/portfolio/dashboard/<user_id>', methods=['GET'])
@token_required
def get_dashboard_data(user_id):
    # Ensure the user ID from the token matches the requested user ID for security
    token_user_id = get_user_id_from_token(request.headers.get('Authorization'))
    if str(user_id) != str(token_user_id):
        abort(403, "Unauthorized access.")

    # Fetch portfolio summary data
    portfolio_summary_response = requests.get(f"{DATABASE_API_URL}/portfolio_summary", params={"user_id": user_id}, timeout=10)
    if portfolio_summary_response.status_code != 200:
        return jsonify({"error": "Unable to fetch portfolio summary."}), portfolio_summary_response.status_code

    portfolio_summary = portfolio_summary_response.json()

    # Fetch detailed stock breakdown for the portfolio
    portfolio_stocks_response = requests.get(f"{DATABASE_API_URL}/portfolio_stocks", params={"user_id": user_id}, timeout=10)
    if portfolio_stocks_response.status_code != 200:
        return jsonify({"error": "Unable to fetch portfolio stocks details."}), portfolio_stocks_response.status_code

    stocks_details = portfolio_stocks_response.json()

    # Construct and return the dashboard data
    dashboard_data = {
        "total_portfolio_value": portfolio_summary.get("total_portfolio_value"),
        "roi": portfolio_summary.get("roi"),
        "stocks_details": stocks_details  # Assuming this is an array of stock information
    }

    return jsonify(dashboard_data), 200


def get_user_portfolio_stocks(user_id):
    try:
        response = requests.get(f"{DATABASE_API_URL}/user_portfolio_stocks/{user_id}", timeout=10)
        if response.status_code == 200:
            portfolio_data = response.json()
            return [stock['symbol'] for stock in portfolio_data.get('stocks', [])]
        else:
            # Log the error or handle it as per your application's error handling policy
            logging.error("Failed to fetch portfolio stocks for user %s. Status code: %s", user_id, response.status_code)
            return []
    except requests.exceptions.RequestException as e:
        # Log the network-related error
        logging.error("Request exception when fetching portfolio stocks for user %s: %s", user_id, e)
        return []

@app.route('/api/portfolio/stocks/performance/<user_id>', methods=['GET'])
@token_required
def get_stocks_performance(user_id):
    try:
        portfolio_stocks = get_user_portfolio_stocks(user_id)
        
        if not portfolio_stocks:
            return jsonify({"error": "No stocks found in the user's portfolio or unable to fetch portfolio."}), 404

        performance_data = {}
        for stock_symbol in portfolio_stocks:
            historical_prices = alpha_vantage_api.get_historical_stock_prices(stock_symbol)
            if historical_prices:
                performance_data[stock_symbol] = historical_prices
            else:
                # Log the specific error for missing historical prices for a stock
                logging.warning(f"No historical price data available for stock {stock_symbol}.")

        if performance_data:
            return jsonify(performance_data), 200
        else:
            return jsonify({"error": "Unable to retrieve stock performance data for any of the portfolio stocks."}), 404
    except Exception as e:
        # Log the unexpected error
        logging.error("Unexpected error in get_stocks_performance for user %s: %s", user_id, e)
        # Send a controlled response indicating an internal server error
        return jsonify({"error": "Internal server error."}), 500

if __name__ == "__main__":
    app.run(debug=True)