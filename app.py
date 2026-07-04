#Need to update code logic for backend application here

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

DB_FILE = "vet_clinic.db"