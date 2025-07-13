from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import asyncio
import yaml
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Bot statistics storage
bot_stats = {
    'servers': 0,
    'total_setups': 0,
    'active_users': 0,
    'template_usage': {
        'default': 0,
        'gaming': 0,
        'professional': 0,
        'educational': 0,
        'minimal': 0
    },
    'recent_activity': [],
    'uptime': datetime.now(),
    'status': 'offline'
}

# Load templates
def load_templates():
    templates_dir = Path("../templates")
    templates = {}
    
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                    template_name = template_file.stem.replace('_template', '')
                    templates[template_name] = template_data
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
    
    return templates

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', stats=bot_stats)

@app.route('/templates')
def templates():
    """Templates management page"""
    templates_data = load_templates()
    return render_template('templates.html', templates=templates_data)

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html', stats=bot_stats)

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    return jsonify(bot_stats)

@app.route('/api/template/<template_name>')
def api_template(template_name):
    """API endpoint for template details"""
    templates_data = load_templates()
    if template_name in templates_data:
        return jsonify(templates_data[template_name])
    return jsonify({'error': 'Template not found'}), 404

@app.route('/api/update_stats', methods=['POST'])
def update_stats():
    """API endpoint to update bot statistics"""
    global bot_stats
    data = request.json
    
    if 'servers' in data:
        bot_stats['servers'] = data['servers']
    if 'total_setups' in data:
        bot_stats['total_setups'] = data['total_setups']
    if 'template_used' in data:
        template = data['template_used']
        if template in bot_stats['template_usage']:
            bot_stats['template_usage'][template] += 1
    if 'activity' in data:
        bot_stats['recent_activity'].insert(0, {
            'timestamp': datetime.now().isoformat(),
            'action': data['activity']
        })
        # Keep only last 100 activities
        bot_stats['recent_activity'] = bot_stats['recent_activity'][:100]
    
    # Emit update to all connected clients
    socketio.emit('stats_update', bot_stats)
    
    return jsonify({'success': True})

@app.route('/api/bot_status/<status>')
def update_bot_status(status):
    """Update bot status"""
    global bot_stats
    bot_stats['status'] = status
    if status == 'online':
        bot_stats['uptime'] = datetime.now()
    
    socketio.emit('status_update', {'status': status, 'uptime': bot_stats['uptime'].isoformat()})
    return jsonify({'success': True})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('stats_update', bot_stats)

@socketio.on('request_stats')
def handle_request_stats():
    """Handle stats request"""
    emit('stats_update', bot_stats)

# Background task to simulate real-time updates
def background_task():
    """Background task for real-time updates"""
    while True:
        time.sleep(30)  # Update every 30 seconds
        # Simulate some activity
        bot_stats['active_users'] = max(0, bot_stats['active_users'] + (-1 if bot_stats['active_users'] > 0 else 1))
        socketio.emit('stats_update', bot_stats)

if __name__ == '__main__':
    # Start background task
    background_thread = threading.Thread(target=background_task)
    background_thread.daemon = True
    background_thread.start()
    
    print("🌐 Dashboard starting at http://localhost:5000")
    print("📊 Real-time analytics enabled")
    print("🔧 Template management available")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
