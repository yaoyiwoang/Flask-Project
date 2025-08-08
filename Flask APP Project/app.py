from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import logging
import os
from datetime import datetime
from config import config

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Sample data
    users_data = [
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'created': '2024-01-01'},
        {'id': 2, 'name': 'Bob', 'email': 'bob@example.com', 'created': '2024-01-02'},
        {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com', 'created': '2024-01-03'}
    ]
    
    messages_data = []
    
    # Template filters
    @app.template_filter('datetime')
    def datetime_filter(date_string):
        """Convert date string to formatted datetime"""
        try:
            dt = datetime.strptime(date_string, '%Y-%m-%d')
            return dt.strftime('%B %d, %Y')
        except:
            return date_string
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        logger.warning(f"404 error for URL: {request.url}")
        return render_template('error.html', 
                             error_code=404, 
                             error_message="The page you're looking for doesn't exist."), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Something went wrong on our end."), 500
    
    # Web Routes
    @app.route('/')
    def home():
        return render_template('index.html', 
                         debug=app.config['DEBUG'],
                         user_count=len(users_data))
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/user/<name>')
    def user_profile(name):
        # Find user in data
        user = next((u for u in users_data if u['name'].lower() == name.lower()), None)
        return render_template('user.html', 
                             username=name, 
                             user_data=user)
    
    @app.route('/users')
    def users_list():
        return render_template('users.html', users=users_data)
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'GET':
            return render_template('contact.html')
        
        elif request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            
            # Validation
            if not all([name, email, message]):
                flash('All fields are required!', 'error')
                return render_template('contact.html')
            
            # Save message
            new_message = {
                'id': len(messages_data) + 1,
                'name': name,
                'email': email,
                'message': message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            messages_data.append(new_message)
            
            logger.info(f"New contact message from {name} ({email})")
            flash('Thank you! Your message has been sent successfully.', 'success')
            
            return redirect(url_for('contact'))
    
    @app.route('/messages')
    def view_messages():
        """Admin view for contact messages"""
        if not app.config['DEBUG']:
            return "Access denied", 403
        return render_template('messages.html', messages=messages_data)
    
    # API Routes
    @app.route('/api/users')
    def api_get_users():
        try:
            search = request.args.get('search', '')
            if search:
                filtered_users = [u for u in users_data 
                                if search.lower() in u['name'].lower() 
                                or search.lower() in u['email'].lower()]
                return jsonify({'users': filtered_users, 'count': len(filtered_users)})
            
            return jsonify({'users': users_data, 'count': len(users_data)})
        
        except Exception as e:
            logger.error(f"API error in get_users: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/users/<int:user_id>')
    def api_get_user(user_id):
        try:
            user = next((u for u in users_data if u['id'] == user_id), None)
            if user:
                return jsonify(user)
            return jsonify({'error': 'User not found'}), 404
        
        except Exception as e:
            logger.error(f"API error in get_user: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/users', methods=['POST'])
    def api_create_user():
        try:
            data = request.get_json()
            
            # Validation
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            if not data.get('name') or not data.get('email'):
                return jsonify({'error': 'Name and email are required'}), 400
            
            # Check for duplicate email
            if any(u['email'].lower() == data['email'].lower() for u in users_data):
                return jsonify({'error': 'Email already exists'}), 409
            
            # Create new user
            new_user = {
                'id': max([u['id'] for u in users_data], default=0) + 1,
                'name': data['name'].strip(),
                'email': data['email'].strip().lower(),
                'created': datetime.now().strftime('%Y-%m-%d')
            }
            users_data.append(new_user)
            
            logger.info(f"Created new user via API: {new_user['name']}")
            return jsonify(new_user), 201
        
        except Exception as e:
            logger.error(f"API error in create_user: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'users_count': len(users_data),
            'messages_count': len(messages_data)
        })
    
    # Debug routes (only in development)
    if app.config['DEBUG']:
        @app.route('/debug/config')
        def debug_config():
            return jsonify({
                'DEBUG': app.config['DEBUG'],
                'SECRET_KEY': app.config['SECRET_KEY'][:10] + '...',
                'HOST': app.config['HOST'],
                'PORT': app.config['PORT']
            })
    
    return app

if __name__ == '__main__':
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    app = create_app()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Flask app in {os.environ.get('FLASK_ENV', 'default')} mode")
    logger.info(f"Server will run on {app.config['HOST']}:{app.config['PORT']}")
    
    app.run(
        host=app.config['HOST'], 
        port=app.config['PORT'], 
        debug=app.config['DEBUG']
    )