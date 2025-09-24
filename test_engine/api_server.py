import threading

from flask import Flask, request, jsonify
from robot import run_cli

app = Flask(__name__)

def run_robot_test(filename):
    run_cli(['--outputdir', 'results', '--listener', 'RobotRedisListener.py', filename], exit=False)

@app.route('/run-test', methods=['POST'])
def run_test():
    # Expecting a file upload with key 'robot_file'
    if 'robot_file' not in request.files:
        return jsonify({'error': 'No .robot file provided'}), 400
    robot_file = request.files['robot_file']
    filename = robot_file.filename
    if not filename.endswith('.robot'):
        return jsonify({'error': 'File must be a .robot file'}), 400
    robot_file.save(filename)
    # Run the test in a background thread
    thread = threading.Thread(target=run_robot_test, args=(filename,))
    thread.start()
    return jsonify({'status': 'Test started in background', 'outputdir': 'results', 'filename': filename})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
