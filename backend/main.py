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