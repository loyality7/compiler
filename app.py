from flask import Flask, request, jsonify, send_from_directory
import requests
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    code = data['code']
    inputs = data['inputs']
    language = data['language']

    # Map languages to OpenFaaS function names
    language_to_faas = {
        'text/x-csrc': 'c-runner',
        'text/x-c++src': 'cpp-runner',
        'text/x-java': 'java-runner',
        'text/x-python': 'python3-runner',
        'text/javascript': 'js-runner'
    }

    # Determine the appropriate runner based on the language
    faas_function = language_to_faas.get(language)

    if not faas_function:
        return jsonify(output="Error: Unsupported language or language not selected."), 400

    # Prepare the payload for the OpenFaaS function
    payload = {
        "code": code,
        "inputs": inputs
    }

    # Log the payload for debugging
    print(f"Sending payload to {faas_function}: {payload}")

    # Send the payload to the OpenFaaS function
    try:
        response = requests.post(f'https://parser.hysterchat.com/function/{faas_function}', json=payload)
        response.raise_for_status()
        output = response.text
    except requests.RequestException as e:
        output = f"Error: {str(e)}"

    # Log the response for debugging
    print(f"Received response: {output}")

    # Return the response from the OpenFaaS function
    return jsonify(output=output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
