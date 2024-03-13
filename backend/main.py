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
