"""
Contract Tracker Flask Application Factory
"""

from flask import Flask
from config import config

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    import os
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Initialize data manager
    from .data.repository import DataManager
    data_manager = DataManager(app.config['DATA_DIR'])
    
    # Register blueprints
    from .api.contracts import contracts_bp
    from .api.dashboard import dashboard_bp
    from .api.custom_holidays import custom_holidays_bp
    from .api.praewood import praewood_bp

    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(custom_holidays_bp)
    app.register_blueprint(praewood_bp)
    
    # Make data manager available to all routes
    app.data_manager = data_manager
    
    return app
