from flask import Flask
import json
import psutil

app = Flask('app')
with open('config.json') as config_file:
    config = json.load(config_file)

@app.route('/cpu')
def cpu_stats():
    return str(psutil.cpu_percent())

@app.route('/ram')
def ram_stats():
    return str(psutil.virtual_memory().percent)

app.run(host='0.0.0.0', port=config["port"])