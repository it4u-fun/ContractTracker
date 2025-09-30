"""
API Blueprint for Contract Tracker
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import API routes
from . import contracts, dashboard
