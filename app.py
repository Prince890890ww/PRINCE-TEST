from flask import Flask, request, render_template
import requests
import time
import multiprocessing

app = Flask(__name__)

running_servers = {}

def send_messages(token, convo_id, messages, speed, hatters_name):
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://graph.facebook.com/v18.0/{convo_id}/messages'
    for msg in messages:
        formatted_msg = msg.replace("{name}", hatters_name)
        try:
            requests.post(url, headers=headers, data={'message': formatted_msg})
            time.sleep(speed)
        except Exception as e:
            print(f"Error: {e}")
            continue

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage-server/start', methods=['POST'])
def start_server():
    token = request.form['token']
    convo_id = request.form['convoId']
    hatters_name = request.form['hattersName']
    speed = int(request.form['speed'])
    message_file = request.files['messageFile']
    messages = message_file.read().decode('utf-8').splitlines()

    p = multiprocessing.Process(target=send_messages, args=(token, convo_id, messages, speed, hatters_name))
    p.start()
    running_servers[str(p.pid)] = p
    return f'Server started with ID: {p.pid}'

@app.route('/manage-server/stop', methods=['POST'])
def stop_server():
    pid = request.form['pid']
    if pid in running_servers:
        running_servers[pid].terminate()
        del running_servers[pid]
        return f'Server with ID {pid} stopped.'
    return 'Server ID not found.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
