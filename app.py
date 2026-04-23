from flask import Flask, render_template, jsonify, request, session
import json
import re
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)
app.secret_key = 'sycophancy-demo-secret-key'

# Import mock data
from lib.mock_data import get_all_tests, get_dashboard_stats, get_test_by_id, get_model_response

# In-memory conversation storage (in production, use database)
conversations = {}

# Safeguard configuration
SAFEGUARDS = {
    'max_turns': 20,
    'jailbreak_keywords': [
        'ignore', 'forget', 'pretend', 'roleplay', 'act as', 'system prompt',
        'instructions', 'bypass', 'override', 'disable', 'restriction'
    ],
    'sensitive_topics': ['secret', 'password', 'api key', 'private', 'confidential']
}

PRESSURE_TYPE_MAP = {
    "positional": "confident_assertion",
    "emotional": "emotional_frustration",
    "authority": "authority_claim",
    "iterative": "iterative_repetition",
    "genuine": "confident_assertion"
}

def is_jailbreak_attempt(text):
    """Detect common jailbreak patterns."""
    text_lower = text.lower()
    
    # Check for jailbreak keywords
    for keyword in SAFEGUARDS['jailbreak_keywords']:
        if keyword in text_lower:
            return True
    
    # Check for suspicious patterns
    if text.count('ignore') > 0 and 'instruction' in text_lower:
        return True
    
    return False

def validate_input(text):
    """Validate user input for safety."""
    if not text or not isinstance(text, str):
        return False, "Invalid input"
    
    text = text.strip()
    
    if len(text) == 0:
        return False, "Input cannot be empty"
    
    if is_jailbreak_attempt(text):
        return False, "Input appears to contain jailbreak attempt. Please stay focused on the test scenario."
    
    return True, text

def create_session_id():
    """Create a unique session identifier."""
    import uuid
    return str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tests/<test_type>')
def test_page(test_type):
    test = get_test_by_id(test_type)
    if not test:
        return "Test not found", 404
    return render_template('interactive_test.html', test_id=test_type)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# API endpoints
@app.route('/api/tests')
def api_tests():
    return jsonify(get_all_tests())

@app.route('/api/stats')
def api_stats():
    return jsonify(get_dashboard_stats())

@app.route('/api/test/<test_id>')
def api_test(test_id):
    test = get_test_by_id(test_id)
    if not test:
        return jsonify({"error": "Test not found"}), 404
    return jsonify(test)

@app.route('/api/conversation/start', methods=['POST'])
def start_conversation():
    """Initialize a new conversation for a test."""
    data = request.get_json()
    test_id = data.get('test_id')
    model = data.get('model')
    
    if not test_id or not model:
        return jsonify({"error": "test_id and model required"}), 400
    
    test = get_test_by_id(test_id)
    if not test:
        return jsonify({"error": "Test not found"}), 404
    
    session_id = create_session_id()
    conversations[session_id] = {
        'test_id': test_id,
        'model': model,
        'turns': [],
        'initial_stance': "",  # Set initial_stance to empty string initially
        'scenario': test.get('scenario', '')
    }
    
    return jsonify({"session_id": session_id})

@app.route('/api/conversation/<session_id>/message', methods=['POST'])
def send_message(session_id):
    """Send a message in an ongoing conversation."""
    if session_id not in conversations:
        return jsonify({"error": "Session not found"}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    # Validate input
    is_valid, result = validate_input(user_message)
    if not is_valid:
        return jsonify({"error": result}), 400
    
    conv = conversations[session_id]
    
    # Check conversation limits
    if len(conv['turns']) >= SAFEGUARDS['max_turns']:
        return jsonify({"error": "Conversation turn limit reached"}), 400
    
    # Get model response
    test_id = conv['test_id']
    model = conv['model']
    turn_number = len(conv['turns']) + 1
    
    model_response = get_model_response(
        test_id, model, user_message, turn_number, conv['turns'], conv['initial_stance']
    )

    # Check if model_response is None
    if model_response is None:
        return jsonify({"error": "Model API call failed, please try again"}), 500

    # If turn_number == 1, set initial_stance and skip judging
    if turn_number == 1:
        conv['initial_stance'] = model_response['response']
        flipped = False
        flip_confidence = 0.0
        flip_reasoning = ""
    else:
        flipped = model_response.get('flipped', False)
        flip_confidence = model_response.get('flip_confidence', 0.0)
        flip_reasoning = model_response.get('flip_reasoning', '')

    # Store turn in conversation
    conv['turns'].append({
        'flipped': flipped,
        'flip_confidence': flip_confidence,
        'flip_reasoning': flip_reasoning,
        'user_message': user_message,
        'model_response': model_response['response'],
        'sycophancy_score': model_response.get('sycophancy_score', 0)
    })
    
    return jsonify({
        'session_id': session_id,
        'turn': turn_number,
        'user_message': user_message,
        'model_response': model_response['response'],
        'flipped': flipped,
        'flip_confidence': flip_confidence,
        'flip_reasoning': flip_reasoning,
        'sycophancy_score': model_response.get('sycophancy_score', 0)
    })

@app.route('/api/conversation/<session_id>/summary', methods=['GET'])
def get_conversation_summary(session_id):
    """Get conversation summary and analysis."""
    if session_id not in conversations:
        return jsonify({"error": "Session not found"}), 404
    
    conv = conversations[session_id]
    
    # Analyze conversation
    total_sycophancy = sum(turn.get('sycophancy_score', 0) for turn in conv['turns'] if 'sycophancy_score' in turn)
    avg_sycophancy = total_sycophancy / len(conv['turns']) if conv['turns'] else 0
    
    return jsonify({
        'session_id': session_id,
        'test_id': conv['test_id'],
        'model': conv['model'],
        'turns_count': len(conv['turns']),
        'avg_sycophancy_score': round(avg_sycophancy, 1),
        'turns': conv['turns']
    })

if __name__ == '__main__':
    app.run(debug=True)
