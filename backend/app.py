"""
CQV Automation Flask Application
Main application entry point
"""

from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db
from routes.assets import assets_bp, ingest_bp
from routes.vdr_rv import vdr_bp, rv_bp

# Create Flask app
app = Flask(__name__)

# Enable CORS for frontend communication
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Register blueprints
app.register_blueprint(assets_bp)
app.register_blueprint(ingest_bp)
app.register_blueprint(vdr_bp)
app.register_blueprint(rv_bp)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CQV Automation Backend',
        'version': '1.0.0'
    })

# Root endpoint
@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'CQV Automation Backend',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'assets': '/api/assets',
            'units': '/api/assets/units',
            'hierarchy': '/api/assets/tag/{tag_id}/hierarchy',
            'control_modules': '/api/assets/tag/{tag_id}/control-modules',
            'ingest': '/api/ingest/b2mml'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    print("Initializing database...")
    init_db()
    print("Database ready!")
    
    # Run development server
    print("\n" + "="*50)
    print("CQV Automation Backend Server")
    print("="*50)
    print("Server: http://localhost:5000")
    print("Health Check: http://localhost:5000/api/health")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
