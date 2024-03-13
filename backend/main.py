# Import necessary libraries and modules
from models import User, Portfolio, PortfolioDetail, Transaction, Stock  # Imports from models.
import logging  # Facilitates logging of messages of various severity levels.
from datetime import datetime, timedelta  # Used for handling dates and time differences.
import re  # Enables regular expression operations.
import requests  # Simplifies making HTTP requests to external services.
import jwt  # Facilitates encoding, decoding, and validation of JWT tokens.
import oracledb  # Additional Oracle database integration, ensure correct import if repetitive.
import os  # Provides a way of using operating system dependent functionality.
from functools import wraps  # Facilitates the use of decorators.
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError # SQLAlchemy specific exception handling.
from sqlalchemy.orm import sessionmaker, declarative_base, joinedload
from flask import Flask, jsonify, request, abort
from flask_cors import CORS  # Allows handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
from flask.views import MethodView
import bcrypt  # Provides password hashing functions.


# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)  # Apply CORS to the entire app for handling browser security restrictions in web applications.

# JWT Secret Key Configuration
# Attempt to fetch the JWT secret key from environment variables; use a fallback for development.
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback_secret_key_for_development')

# Authentication Decorator Function
# This decorator is used to ensure that routes are accessible only with a valid JWT token.
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Attempt to retrieve the JWT token from the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        # If no token is found in the request, return an error response
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the token using the secret key to validate it
            jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            # If token validation fails, return an invalid token error
            return jsonify({'message': 'Token is invalid!'}), 403

        # Proceed with the original function if the token is valid
        return f(*args, **kwargs)
    return decorated_function

# Utility Function to Get User ID from JWT Token
# This function extracts and returns the user ID from a provided JWT token.
def get_user_id_from_token(token):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return decoded_token.get("user_id")
    except jwt.ExpiredSignatureError:
        abort(401, 'Token has expired.')  # Handle expired token
    except jwt.InvalidTokenError:
        abort(401, 'Invalid token.')  # Handle invalid token

# Oracle Database Initialization
# Initializes the Oracle client using the specified library directory. This step is necessary for Oracle database operations.
oracledb.init_oracle_client(lib_dir=r"C:\\Program Files\\Oracle\\instanclient-basic-windows.x64-21.13.0.0.0dbru\\instantclient_21_13")

# Database Credentials and Connection String
# These variables store the database username, password, and DSN (Data Source Name) for connecting to the Oracle database.
# It's highly recommended to manage sensitive data like usernames and passwords securely, for example, via environment variables.
un = 'DEVELOPER'  # Database username
pw = 'AngeleeRiosRamon1999!'  # Database password - consider using a more secure approach for production
dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd51c296542b64f_version3_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(f'oracle+cx_oracle://{un}:{pw}@{dsn}')
Session = sessionmaker(bind=engine)


def hash_password(plain_text_password):
    """
    Hashes a plaintext password using bcrypt.

    Args:
        plain_text_password (str): The plaintext password to hash.

    Returns:
        str: The hashed password, encoded in utf-8 and suitable for storage in the database.

    This function takes a plaintext password as input, hashes it using bcrypt to ensure security,
    and then returns the hashed password. The bcrypt algorithm automatically handles salt generation
    and storage as part of the hash value, providing strong security against rainbow table and
    brute-force attacks.
    """
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def is_password_valid(password):
    """
    Validates a password against specified criteria.

    Args:
        password (str): The password to validate.

    Returns:
        bool: True if the password meets the criteria, False otherwise.

    The criteria for a valid password in this application are:
    - At least 8 characters long.
    - Contains at least one lowercase letter.
    - Contains at least one uppercase letter.
    - Contains at least one digit.
    - Contains at least one special character (e.g., !@#$%^&*(),.?":{}|<>).

    This function uses regular expressions to check if the provided password meets
    all the above criteria, ensuring a baseline level of password complexity and security.
    """
    return len(password) >= 8 and re.search("[a-z]", password) and re.search("[A-Z]", password) and re.search("[0-9]", password) and re.search("[!@#$%^&*(),.?\":{}|<>]", password)

class AlphaVantageAPI:
    """
    A class for interacting with the Alpha Vantage API to retrieve stock market data.
    
    Attributes:
        api_key (str): The API key used for authenticating requests to Alpha Vantage.
        base_url (str): The base URL for the Alpha Vantage API endpoints.
    """

    def __init__(self, api_key):
        """
        Initializes the AlphaVantageAPI instance with an API key and sets the base URL.
        
        Args:
            api_key (str): The API key for Alpha Vantage.
        """
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query?"

    def make_request(self, params):
        """
        Makes a request to the Alpha Vantage API with the given parameters.
        
        Args:
            params (dict): The parameters to include in the request.
        
        Returns:
            dict: The JSON response from the API, or None if an error occurs.
        """
        params['apikey'] = self.api_key  # Append the API key to the request parameters
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Request exception: %s", e)
            return None

    def get_stock_final_price(self, symbol):
        """
        Retrieves the most recent closing price for a given stock symbol.
        
        Args:
            symbol (str): The stock symbol to query.
        
        Returns:
            float: The most recent closing price of the stock, or None if not found.
        """
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
        """
        Fetches historical stock prices for the given symbol for the last year.
        
        Args:
            symbol (str): The stock symbol to query.
        
        Returns:
            dict: A dictionary of historical prices, where keys are dates and values are closing prices.
        """
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


ALPHA_VANTAGE_API_KEY = "ZBD3QIPITMQNSPPF"

# Initialize an instance of the AlphaVantageAPI class with your API key
alpha_vantage_api = AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)

@app.route('/handle_register', methods=['POST'])
def api_register_user():
    """
    Registers a new user with the provided username and password. Upon successful registration,
    a new portfolio is created for the user, and a JWT token is generated and returned for immediate authentication.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    hashed_password = hash_password(password)
    session = Session()

    try:
        # Check if the username already exists to prevent duplicate registrations.
        existing_user = session.query(User).filter_by(NAME=username).first()
        if existing_user:
            return jsonify({"error": "Username already exists."}), 409
        
        # Create and add the new user to the database.
        new_user = User(NAME=username, HASHED_PASSWORD=hashed_password)
        session.add(new_user)
        session.flush()  # Flush the session to get the newly created User ID.

        # Create a new portfolio for the user.
        new_portfolio = Portfolio(USERID=new_user.ID, TOTALPORTFOLIOVALUE=0, TOTALROI=0)
        session.add(new_portfolio)

        session.commit()

        # Generate a JWT token for the new user.
        token = jwt.encode({
            'user_id': new_user.ID,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, JWT_SECRET_KEY, algorithm="HS256")

        return jsonify({"message": "User registered successfully.", "token": token.decode('UTF-8')}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Username already exists."}), 409
    except Exception as e:
        session.rollback()
        logging.error(f"Unexpected error during registration: {e}")
        return jsonify({"error": "Registration failed due to an unexpected error."}), 500
    finally:
        session.close()

    
@app.route('/handle_login', methods=['POST'])
def login_user():
    """
    Authenticates a user by their username and password. If authentication is successful,
    generates and returns a JWT token for the user to use in subsequent authenticated requests.

    Accepts:
        JSON payload with 'username' and 'password'.

    Returns:
        On successful authentication: A JWT token in the response body.
        On failure: An error message indicating either incorrect credentials or a server issue.
    """
    # Extract login credentials from the request body.
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Begin a new session for database operations.
    session = Session()
    try:
        # Attempt to fetch the user by the provided username.
        user = session.query(User).filter_by(NAME=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.HASHED_PASSWORD.encode('utf-8')):
            # If the user is found and the password is correct, generate a JWT token.
            token = jwt.encode({
                'user_id': user.ID,
                'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day.
            }, JWT_SECRET_KEY, algorithm="HS256")

            # Return the token to the user.
            return jsonify({'token': token.decode('UTF-8')}), 200
        else:
            # If the user is not found or the password is incorrect, return an error.
            return jsonify({'error': 'Invalid username or password'}), 401
    except SQLAlchemyError as sae:
        # Handle potential SQLAlchemy errors during the user fetch operation.
        session.rollback()
        logging.error(f"SQLAlchemy Error during login: {sae}")
        return jsonify({"error": "An error occurred during login."}), 500
    finally:
        # Ensure the session is always closed after the operation.
        session.close()
    
class UserPortfolioAPI(MethodView):
    """
    Fetches and returns the portfolio details for a specific user, including total value,
    return on investment (ROI), and details of each stock within the portfolio.
    """
    
    def get(self, user_id):
        """
        Retrieves portfolio information for a specified user ID.
        
        Args:
            user_id (int): The ID of the user whose portfolio information is being requested.
        
        Returns:
            A JSON response containing the portfolio details or an error message.
        """
        session = Session()
        try:
            # Fetch the user's portfolio based on the user_id. Utilize joinedload for eager loading of related entities.
            user_portfolio = session.query(Portfolio).options(joinedload(Portfolio.details)).filter_by(USERID=user_id).first()
            
            if not user_portfolio:
                return jsonify({"error": "Portfolio not found."}), 404

            # Compile details of each stock within the portfolio
            stocks_details = [
                {
                    "symbol": detail.TICKERSYMBOL,
                    "quantity": detail.QUANTITY,
                    "last_closing_price": detail.LASTCLOSINGPRICE,
                    "total_stock_value": detail.TOTALSTOCKVALUE
                }
                for detail in user_portfolio.details
            ]

            # Construct and return the aggregated data
            portfolio_data = {
                "total_portfolio_value": user_portfolio.TOTALPORTFOLIOVALUE,
                "roi": user_portfolio.TOTALROI,
                "stocks_details": stocks_details
            }

            return jsonify(portfolio_data)
        except SQLAlchemyError as e:
            # Log any SQLAlchemy errors encountered during the query.
            logging.error(f"SQLAlchemy Error: {e}")
            return jsonify({"error": "An error occurred fetching portfolio details."}), 500
        finally:
            # Ensure the session is closed after processing.
            session.close()

# Register the view function for the endpoint.
user_portfolio_view = UserPortfolioAPI.as_view('user_portfolio_api')
app.add_url_rule('/api/users/<int:user_id>/portfolio', view_func=user_portfolio_view, methods=['GET'])

class AssetDetailsAPI(MethodView):
    """
    Fetches and returns detailed asset information for a specific user, including historical stock prices.
    """

    def get(self, user_id):
        """
        Retrieves detailed asset information for a specified user ID, including historical stock prices.
        
        Args:
            user_id (int): The ID of the user whose asset details are being requested.
        
        Returns:
            A JSON response containing detailed asset information or an error message.
        """
        session = Session()
        try:
            # Fetch the user's portfolio details, including stocks, using ORM relationships.
            portfolio = session.query(Portfolio).options(joinedload(Portfolio.details)).filter_by(USERID=user_id).first()

            if not portfolio:
                return jsonify({"error": "Portfolio not found."}), 404

            # Initialize an instance of the AlphaVantageAPI for fetching historical stock prices.
            alpha_vantage_api = AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)
            stocks_details = []

            for detail in portfolio.details:
                # Fetch historical stock prices for each stock in the portfolio.
                historical_prices = alpha_vantage_api.get_historical_stock_prices(detail.TICKERSYMBOL)

                stocks_details.append({
                    "symbol": detail.TICKERSYMBOL,
                    "quantity": detail.QUANTITY,
                    "historical_prices": historical_prices
                })

            # Aggregate and return detailed asset information.
            response = {
                "total_portfolio_value": portfolio.TOTALPORTFOLIOVALUE,
                "stocks_details": stocks_details
            }

            return jsonify(response)
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemy Error: {e}")
            return jsonify({"error": "An error occurred fetching asset details."}), 500
        finally:
            session.close()

# Register the view function for the endpoint.
asset_details_view = AssetDetailsAPI.as_view('asset_details_api')
app.add_url_rule('/api/assets/<int:user_id>', view_func=asset_details_view, methods=['GET'])

class StockTransactionAPI(MethodView):
    """
    A view class handling stock transactions, including buying and selling (removing) stock for a user's portfolio.
    """

    def buy_stock(self, user_id, symbol, quantity, purchase_price):
        """
        Adds a specified quantity of a stock to the user's portfolio and creates a corresponding transaction record.
        """
        session = Session()
        try:
            # Retrieve the associated user
            user = session.query(User).filter(User.ID == user_id).one()

            # Find or create a stock entry for the user
            stock = session.query(Stock).filter(Stock.USER_ID == user_id, Stock.SYMBOL == symbol).first()
            if stock:
                # Update existing stock
                stock.SHARES += quantity
                # Assuming purchase price is an update to the purchase price
                stock.PURCHASE_PRICE = purchase_price
            else:
                # Create a new stock entry
                stock = Stock(USER_ID=user_id, SYMBOL=symbol, SHARES=quantity, PURCHASE_PRICE=purchase_price)
                session.add(stock)
            
            # Assuming PortfolioDetail and Transaction update
            portfolio_detail = session.query(PortfolioDetail).filter(
                PortfolioDetail.PORTFOLIOID == user.portfolios[0].PORTFOLIOID, 
                PortfolioDetail.TICKERSYMBOL == symbol
            ).first()

            if portfolio_detail:
                portfolio_detail.QUANTITY += quantity
            else:
                # Create new portfolio detail if it doesn't exist
                portfolio_detail = PortfolioDetail(
                    PORTFOLIOID=user.portfolios[0].PORTFOLIOID,
                    TICKERSYMBOL=symbol,
                    QUANTITY=quantity,
                    LASTCLOSINGPRICE=purchase_price,  # This field might require updating depending on actual transaction logic
                    TOTALSTOCKVALUE=quantity * purchase_price  # Simplified calculation
                )
                session.add(portfolio_detail)

            # Record the transaction
            transaction = Transaction(
                PORTFOLIOID=user.portfolios[0].PORTFOLIOID,
                SYMBOL=symbol,
                TRANSACTIONDATE=datetime.now(),
                QUANTITY=quantity,
                TRANSACTIONPRICE=purchase_price,
                CURRENTTOTALVALUE=quantity * purchase_price,  # Simplified calculation
                TRANSACTIONTYPE='buy'
            )
            session.add(transaction)

            session.commit()
            return jsonify({"message": f"Successfully added {quantity} shares of {symbol}."}), 200
        except Exception as e:
            session.rollback()
            logging.error(f"Failed to add stock: {e}")
            return jsonify({"error": "Failed to add stock."}), 500
        finally:
            session.close()


    def remove_stock(self, user_id, symbol):
        """
        Removes all shares of a specified stock from the user's portfolio and adjusts the portfolio value accordingly.
        """
        session = Session()
        try:
            # Retrieve the stock entry
            stock = session.query(Stock).filter(Stock.USER_ID == user_id, Stock.SYMBOL == symbol).one()

            # Adjust the portfolio value (simplified logic; adjust as per actual business logic)
            user = session.query(User).filter(User.ID == user_id).one()
            portfolio = user.portfolios[0]  # Assuming one portfolio per user
            portfolio.TOTALPORTFOLIOVALUE -= stock.SHARES * stock.PURCHASE_PRICE

            # Record the transaction
            transaction = Transaction(
                PORTFOLIOID=portfolio.PORTFOLIOID,
                SYMBOL=symbol,
                TRANSACTIONDATE=datetime.now(),
                QUANTITY=-stock.SHARES,  # Negative quantity for removal
                TRANSACTIONPRICE=stock.PURCHASE_PRICE,
                CURRENTTOTALVALUE=-stock.SHARES * stock.PURCHASE_PRICE,  # Negative value for removal
                TRANSACTIONTYPE='sell'
            )
            session.add(transaction)

            # Remove the stock entry
            session.delete(stock)

            session.commit()
            return jsonify({"message": f"Successfully removed all shares of {symbol}."}), 200
        except Exception as e:
            session.rollback()
            logging.error(f"Failed to remove stock: {e}")
            return jsonify({"error": "Failed to remove stock."}), 500
        finally:
            session.close()

            
# Route for adding stocks to a user's portfolio
@app.route('/users/<int:user_id>/stocks/add', methods=['POST'])
def add_stocks(user_id):
    """
    Endpoint for adding stocks to a user's portfolio. Accepts JSON data specifying the stock symbol and quantity.
    """
    data = request.json
    symbol = data['symbol']
    quantity = data['quantity']
    result, status = StockTransactionAPI().buy_stock(user_id, symbol, quantity)
    return jsonify(result), status

# Route for removing stocks from a user's portfolio
@app.route('/users/<int:user_id>/stocks/remove', methods=['POST'])
def remove_stocks(user_id):
    """
    Endpoint for removing all shares of a specific stock from a user's portfolio.
    """
    data = request.json
    symbol = data['symbol']
    result, status = StockTransactionAPI().remove_stock(user_id, symbol)
    return jsonify(result), status

if __name__ == "__main__":
    app.run(debug=True)