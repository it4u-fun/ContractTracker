"""
Contract Tracker Flask Application Factory
"""

from flask import Flask
from config import config

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize data manager
    from .data.repository import DataManager
    data_manager = DataManager(app.config['DATA_DIR'])
    
    # Register blueprints
    from .api.contracts import contracts_bp
    from .api.dashboard import dashboard_bp
    
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Make data manager available to all routes
    app.data_manager = data_manager
    
    return app
