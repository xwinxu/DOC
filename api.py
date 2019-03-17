#!/usr/bin/env python3
import random
from random import shuffle
import time
from tqdm import tqdm
from multiprocessing import Process
import speech_recognition as sr
from model.MVG import MVG

from flask import Flask, jsonify, session, request


LOG_FILE = "log"


app = Flask("doc")
alphabet = [str(ch) for ch in range(ord('a'), ord('z'))]
message = ""
diagnosis = ""
process = None

# Gaussian prediction model
mvg = MVG()
mvg.create_model()


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/starttrans')
def get_start_transcription():
    # listen and print to text file
    global process
    if process is None:
        process = Process(target=transcribe)
        process.start()
    return jsonify({})


@app.route('/stoptrans')
def get_stop_transcription():
    # send signal to process and kill it
    global process
    if process is not None:
        process.terminate()
        process = None
    return jsonify({})


@app.route('/spectrum', methods=["GET"])
def get_spectrum():
    return jsonify(
        [random.randint(0, 200) for _ in range(512)]
    )


@app.route('/transcript', methods=["GET"])
def get_transcript():
    ret = {}
    with open(LOG_FILE, "r") as file:
        for line in file.readlines():
            split = line.split("\t")
            ret[split[0]] = split[1]
    return jsonify(ret)


@app.route('/diseases', methods=["GET"])
def get_diseases():
    print(message)
    sentence = message
    with open(LOG_FILE, "r") as file:
        for line in file.readlines():
            split = line.split("\t")
            sentence += split[1]
    return jsonify(mvg.predict(sentence))


@app.route('/recommendations', methods=["GET"])
def get_recommendations():
    return jsonify(mvg.get_questions())


@app.route('/correlations', methods=["GET"])
def get_correlations():
    ret = {}
    for i in range(200):
        shuffle(alphabet)
        disease1 = ''.join(alphabet)
        shuffle(alphabet)
        disease2 = ''.join(alphabet)
        correlation = random.randint(1, 11)
        ret[((disease1, disease2))] = correlation
    return jsonify(ret)


@app.route('/sendnotes', methods=["POST"])
def send_notes():
    global message
    message = list(request.form.to_dict(flat=False).keys())[0]
    print(message)
    if message == "EMPTY":
        message = ""
    return jsonify({})


@app.route("/senddiagnosis", methods=["POST"])
def send_diagnosis():
    global diagnosis
    diagnosis = list(request.form.to_dict(flat=False).keys())[0]
    if diagnosis == "EMPTY":
        diagnosis = ""
    return jsonify({})

"""
Speech to text recognition using google voice
"""
def transcribe():
    r = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        text = r.recognize_sphinx(audio)
        with open(LOG_FILE, "a+") as file:
            # want time to the closest whole number
            file.write("{:.0f}\t{}\n".format(time.time(), text))


if __name__ == "__main__":
    app.run(debug=True)
