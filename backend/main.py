from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging
import requests
import bcrypt
from datetime import datetime, timedelta
import re
import jwt
import os
import cx_Oracle as oracledb
import oracledb
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from models import db, initialize_database, Users, Portfolios, PortfolioDetails, Transactions
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask.views import MethodView
from sqlalchemy.orm import joinedload
from alpha_vantage import AlphaVantageAPI

oracledb.init_oracle_client(lib_dir=r"C:\\Program Files\\Oracle\\instanclient-basic-windows.x64-21.13.0.0.0dbru\\instantclient_21_13")


un = 'DEVELOPER'
pw = 'AngeleeRiosRamon1999!'  # Replace with your actual password
dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd51c296542b64f_projectdb22023_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"# Replace with your actual DSN

DATABASE_API_URL = "https://gd51c296542b64f-projectdb22023.adb.eu-madrid-1.oraclecloudapps.com/ords/"

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)
app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+cx_oracle://{un}:{pw}@{dsn}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

initialize_database(app)

ALPHA_VANTAGE_API_KEY = "ZBD3QIPITMQNSPPF"

alpha_vantage_api = AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def is_password_valid(password):
    return len(password) >= 8 and re.search("[a-z]", password) and re.search("[A-Z]", password) and re.search("[0-9]", password) and re.search("[!@#$%^&*(),.?\":{}|<>]", password)


# Define a route for handling registration requests
@app.route('/handle_register', methods=['POST'])
def api_register_user():
    # Extract data from the incoming request
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    # Validate the provided password against your criteria (not shown in this snippet)
    if not is_password_valid(password):
        # If the password does not meet your criteria, return a 400 error
        return jsonify({"error": "Password does not meet the security criteria."}), 400

    # Check if a user with the provided email already exists
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        # If a user with this email already exists, return a 409 conflict error
        return jsonify({"error": "Email already exists."}), 409

    # Hash the provided password for secure storage
    password_hash = hash_password(password)

    # Create a new user instance with the provided and processed data
    new_user = Users(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash
    )

    try:
        # Attempt to add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        # If successful, return a message indicating successful registration along with the new user's ID
        return jsonify({"message": "User registered successfully.", "user_id": new_user.user_id}), 201
    except IntegrityError:
        # If an integrity error occurs (e.g., duplicate username or email not caught by earlier checks), roll back the transaction
        db.session.rollback()
        return jsonify({"error": "Username or email already exists."}), 409
    except Exception as e:
        # For any other exceptions, log the error, roll back the transaction, and return a 500 internal server error
        db.session.rollback()
        logging.error("Error registering user: %s", e)
        return jsonify({"error": "Error registering user."}), 500
