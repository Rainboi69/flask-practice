from flask import Flask
import time

app = Flask(__name__)

@app.route("/nutrition/eggs")
def eggs():
    time.sleep(1)
    return {"food": "eggs", "protein": 6}

@app.route("/nutrition/slow-eggs")
def slow_eggs():
    time.sleep(5)
    return {"food": "eggs", "protein": 6}

if __name__ == "__main__":
    app.run(port=5001)