import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
from tensorflow.python.framework import ops
import random
import json
import pickle
import pyfiglet
import os
import pyttsx3
engine = pyttsx3.init()
engine.setProperty("rate", 180)
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[4].id)

with open("intents.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)


ops.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 40)
net = tflearn.fully_connected(net, 40)
net = tflearn.fully_connected(net, 40)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)


model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=30000, batch_size=10, show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def chat():
    os.system('cls||clear')
    print("\n\n\n\n")
    ascii_banner = pyfiglet.figlet_format("javascriptcoding")
    print(ascii_banner)
    print("\n\n")
    # engine.say("Willkommen zurück, Sir!")
    engine.say("Welcome back, Sir!")
    engine.runAndWait()
    while True:
        inp = input("You: ")

        results = model.predict([bag_of_words(inp, words)])[0]
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if results[results_index] > 0.8:
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg["responses"]

            answer = random.choice(responses)
            print("Chatbot: " + answer)
            engine.say(answer)
            engine.runAndWait()

            if tag == "abschied":
                break
        else:
            engine.say("Ich habe nicht ganz verstanden, was du meinst.")
            engine.runAndWait()

chat()
