from flask import Flask
from flask import request
import sys, os
from data import processData
import json

app = Flask(__name__)

TRANSCRIPT_PATH = "data/transcript.txt"

@app.route("/load_data")
def return_data():
    return str(processData.load_all())

@app.route("/save_transcript")
def save_transcript():
    data = request.args.get("data")

    if data != None:
        f = open(TRANSCRIPT_PATH, '+a')
        f.write("{}:{}\n\n".format(data['time'], data['text']))
    else:
        print("No data")

@app.route("/get_transcript")
def get_transcript():
    if os.path.isfile(TRANSCRIPT_PATH):
        return open(TRANSCRIPT_PATH, 'r').read()
    else:
        return "No data yet"

@app.route("/save_diagnosis")
def save_diagnosis():
    saved_data = {}
    if os.path.isfile(processData.SAVED_DATA_PATH):
        saved_data = pickle.load(open(processData.SAVED_DATA_PATH, 'rb'))
    else:
        return "No data"

    data = request.args.get("data")

    diag = data["diagnosis"]
    symps = data["symptoms"].lower().spllit(' ')

    val = saved_data.get(diag, [])
    val.append(symps)
    saved_data[diag] = val

    pickle.dump(saved_data, open(processData.SAVED_DATA_PATH, "rb"))

if __name__ == "__main__":
    app.run(debug=True)
