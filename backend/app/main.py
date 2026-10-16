from flask import Flask, request, jsonify
from flask_cors import CORS
from app.experimentation_pipelines.base_localization.backend import get_response_from_backend_exp1
from app.experimentation_pipelines.adaptive_profile.backend import get_response_from_backend_exp2
from app.experimentation_pipelines.text_reformulation.backend import get_response_from_backend_exp3
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import datetime
import json
from pathlib import Path

# take statics from env 

USERS_FILE = Path(__file__).with_name("users.json")

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

app = Flask(__name__)
CORS(app)  
loggedin_user = 'guest'


def load_users():  
    with USERS_FILE.open('r') as f:
        return json.load(f)  
  
def save_users(users):  
    with USERS_FILE.open('w') as f:
        json.dump(users, f, indent=4)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

    users = load_users()
    
    if username in users :
        if users[username] == password:
            loggedin_user = username
            return jsonify({'status': 'success', 'message': 'Login successful'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid credentials. Please try again.'}), 401
    else:
        return jsonify({'status': 'error', 'message': 'User not found. Please register.'}), 401


@app.route('/register', methods=['POST']) 
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
        
    users = load_users()
    
    if username in users:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 401
        
    users[username] = password
    save_users(users)
    
    return jsonify({'status': 'success', 'message': 'Registration successful'})


@app.route('/gateway', methods=['POST'])
def predict():
    query_parameters = request.json
    backend_endpoint = request.args.get('backend_endpoint') or 'backend_exp1'
    env = request.args.get('env')

    # ===== ADD THESE DEBUG LINES =====  
    print("ARGS:", dict(request.args))                 # shows query params (?backend_endpoint=...)  
    print("backend_endpoint =", backend_endpoint)  
    print("env =", env)  
    print("BODY keys:", list(query_parameters.keys()) if query_parameters else None)  
    # ================================= 
        
    if backend_endpoint == 'backend_exp1':
        response = get_response_from_backend_exp1(query_parameters)
    elif backend_endpoint == 'backend_exp2':
        response = get_response_from_backend_exp2(query_parameters)
    elif backend_endpoint == 'backend_exp3':
        response = get_response_from_backend_exp3(query_parameters)
    else :
        response = None

    # ===== AND HERE =====  
    print("RESPONSE:", response)   # will print None if routing failed  
    # =====================  

    if env != 'prod':    
        return jsonify(response)
    

    log_entry = {
        'username': loggedin_user,
        'timestamp': datetime.datetime.utcnow(),
        'backend_endpoint': backend_endpoint,
        'query_parameters': query_parameters,
        'response': response
    }
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['user_data']
        collection = db['user_data']
        collection.insert_one(log_entry)

    except Exception as e:
        print("Failed to launch database",str(e))

    return jsonify(response)
    

@app.route('/chrome-api', methods=['POST'])
def chrome_extension():

    query_parameters = request.json

    query_parameters['type'] = 'fresh'
    query_parameters['country'] = 'USA' if query_parameters['country'] == '' else query_parameters['country']
    query_parameters['age_group'] = 'Adult (18+)' if query_parameters['age_group'] == '' else query_parameters['age_group']
    query_parameters['region'] = 'Urban' if query_parameters['country'] == '' else query_parameters['country']
    query_parameters['messages'] = []
    query_parameters['political_awareness'] = 'No'
    query_parameters['education_level'] = 'Primary'
    query_parameters['literature_preference'] = 'English'
    query_parameters['food_cuisine'] = 'American'
    url = query_parameters['url']
    query_parameters['text'] = extract_text_from_url(url)

    response = get_response_from_backend_exp1(query_parameters)
    entities = response['annotations_response']['annotations'][0][1]['entities']
    explanations = response['explanations']
    text = response['annotations_response']['annotations'][0][0]
    
    response_chrome = []
    for i, entity in enumerate(entities):
        response_chrome.append(
            {
                "word": text[entity[0]:entity[1]+1],
                "familiarity" : entity[2].lower(),
                "meaning": explanations[i]["explanation"]
        })

    response_chrome = jsonify(response_chrome)
    return response_chrome

@app.route('/live')
def health():
    return {"health_status":"live"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = 8081, debug=True)