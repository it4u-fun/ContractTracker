#!/usr/bin/env python3
"""
Main application entry point for Contract Tracker.
"""

import os
import sys
from flask import Flask, render_template

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from config import config

def create_web_app():
    """Create the Flask web application with routes."""
    app = create_app('development')
    
    @app.route('/')
    def index():
        """Main dashboard page."""
        return render_template('dashboard/index.html')
    
    @app.route('/contracts')
    def contracts_index():
        """Contracts index page."""
        return render_template('contracts/index.html')
    
    @app.route('/contracts/new')
    def new_contract():
        """New contract page."""
        return render_template('contracts/new.html')
    
    @app.route('/contracts/<contract_key>')
    def contract_detail(contract_key):
        """Contract detail page."""
        return render_template('contracts/detail.html', contract_key=contract_key)
    
    @app.route('/contracts/<contract_key>/calendar')
    def contract_calendar(contract_key):
        """Contract calendar page."""
        return render_template('contracts/calendar.html', contract_key=contract_key)
    
    @app.route('/settings')
    def settings():
        """Settings page."""
        return render_template('settings/index.html')
    
    @app.route('/learn')
    def learn():
        """Learning/Onboarding page for repo usage and evolution plan."""
        return render_template('learn/index.html')
    
    @app.route('/api')
    def api_info():
        """API information page."""
        from flask import jsonify
        return jsonify({
            "message": "Contract Tracker API",
            "version": "1.0.0",
            "endpoints": {
                "dashboard": "/api/dashboard/",
                "contracts": "/api/contracts/",
                "settings": "/api/dashboard/settings"
            },
            "documentation": "/api/docs",
            "status": "running"
        })
    
    return app

# Create the app instance for gunicorn
app = create_web_app()

# Ensure data directory exists when app starts
with app.app_context():
    data_dir = config['development'].DATA_DIR
    os.makedirs(data_dir, exist_ok=True)

if __name__ == '__main__':
    print("Starting Contract Tracker...")
    print(f"Data directory: {data_dir}")
    print("Open your browser to: http://localhost:5000")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
