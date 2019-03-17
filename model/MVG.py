from processData import load_UMLS
from math import log
from gensim.models import KeyedVectors
import numpy as np
import pickle
import os
from scipy.stats import multivariate_normal
from gensim.scripts.glove2word2vec import glove2word2vec

filename = 'GoogleNews-vectors-negative300.bin'
filename = 'glove.6B.50d.txt.word2vec'

def compute_means(x, y):
    means = np.zeros((y.shape[1], x.shape[1]))
    for k in range(y.shape[1]):
        x_data = []
        for i in range(y.shape[0]):
            if bool(y[i][k]):
                x_data.append(x[i])

        means[k] = np.mean(x_data, axis=0)

    return means


def compute_cov(x, y):
    covariances = np.zeros((y.shape[0], x.shape[1], x.shape[1]))
    print(y.shape)

    for k in range(y.shape[1]):
        x_data = []
        for i in range(y.shape[0]):
            if bool(y[i][k]):
                x_data.append(x[i])

        covariances[k] = np.cov(np.array(x_data).transpose())

    return covariances

class MVG:
    def __init__(self):
        self._keywords = []
        self.output_encoding = {}
        self.output_to_word = {}
        self.MAX_KEYWORDS = 1000
        self.MAX_QUESTIONS = 4
        self.MAX_DATA = 20
        print("Loading encoders...")
        self.encoder = KeyedVectors.load_word2vec_format(filename, binary=False)
        print("Done!")
        self.output_probs = {}
        self.output_importance = {}
        self.mean = np.array([])
        self.covariances = np.array([])
        self.total_data = []
        self.smoothing_factor = 0.3

    def get_all_words(self, mapping):
        all_words = set([])
        for key, item in mapping.items():
            for symptom_sets in item["symptoms"]:
                for word in symptom_sets:
                    if word != '':
                        all_words.add(word.lower())

        return list(all_words)

    def parse_for_keywords(self, words):
        return [w.lower() for w in words if w.lower() in self._keywords]

    def setup_probs(self, mapping):
        total = sum([x['count'] for x in mapping.values()])
        for disease, symptom_sets in mapping.items():
            self.output_probs[disease] = symptom_sets['count'] / total

    def encode_data(self, mapping):
        y = []
        x = []

        if x != [] and y != []:
            return np.array(x), np.array(y)

        for disease, symptom_sets in mapping.items():
            for symp in symptom_sets['symptoms']:
                for s in symp:
                    try:
                        x.append(self.encoder.get_vector(s))
                        y.append(self.output_encoding[disease])
                    except Exception as e:
                        print(e)
                        continue

        return np.array(x), np.array(y)

    def encode_output(self, mapping):
        length = len(mapping.keys())
        count = 0
        for disease in mapping.keys():
            self.output_encoding[disease] = np.array([int(i==count) for i in range(length)])
            self.output_to_word[count] = disease
            count += 1

    def train(self, mapping):
        #first set keywords to look for
        all_words = self.get_all_words(mapping)
        self.setup_probs(mapping)

        if len(all_words) > self.MAX_KEYWORDS:
            self._keywords = self.entropy_parse_keywords(mapping)
        else:
            self._keywords = list(all_words)
            self.entropy_parse_keywords(mapping)

        self.encode_output(mapping)

        x, y = self.encode_data(mapping)

        means = compute_means(x, y)
        covariances = compute_cov(x, y)

        self.means = means
        for k in range(covariances.shape[0]):
            covariances[k] += np.eye(covariances[k].shape[0])
        self.covariances = covariances*0.5

    def entropy_parse_keywords(self, mapping):
        all_words = self.get_all_words(mapping)
        IG_word = []
        for word in all_words:
            IG = self.calc_information_gain(mapping, word)
            IG_word.append((IG, word))
            self.output_importance[word] = IG

        return [x for x in sorted(IG_word)[len(IG_word) - self.MAX_KEYWORDS:]]

    def calc_information_gain(self, mapping, keyword):
        parent_entropy = 0

        total_examples = sum(map(lambda x: len(x['symptoms']), list(mapping.values())))

        for disease, symptom_sets in mapping.items():
            occurences = len(symptom_sets['symptoms'])
            if occurences != 0:
                parent_entropy -= occurences / total_examples * log(occurences / total_examples)

        child_1_total_examples = 0
        child_2_total_examples = 0
        child_1_entropy = 0
        child_2_entropy = 0

        for disease, symptom_sets in mapping.items():
            occurences = len([x for x in symptom_sets['symptoms'] if keyword in x])
            counter_occurences = len(symptom_sets['symptoms']) - occurences
            child_1_total_examples += occurences
            child_2_total_examples += counter_occurences

        for disease, symptom_sets in mapping.items():
            occurences = len([x for x in symptom_sets['symptoms'] if keyword in x])
            counter_occurences = len(symptom_sets['symptoms']) - occurences
            if occurences != 0:
                child_1_entropy -= occurences / child_1_total_examples * log(occurences / child_1_total_examples)
            if counter_occurences != 0:
                child_2_entropy -= counter_occurences / child_2_total_examples * log(counter_occurences / child_2_total_examples)

        IG = parent_entropy - child_1_total_examples / total_examples * child_1_entropy \
                                - child_2_total_examples / total_examples * child_2_entropy

        print("Information gain for {} is {}".format(keyword, IG))

        return IG

    def predict(self, sentence):
        words = sentence.lower().replace(",",'').replace(".",'').replace('-',' ').split(" ")

        sentence_outputs = []
        for word in words:
            try:
                encoding = self.encoder.get_vector(word)
                y = self.classify_data(encoding, self.means, self.covariances)
                self.total_data.append(encoding)

                if len(self.total_data) > self.MAX_DATA:
                    self.total_data = self.total_data[1:]
            except Exception as e:
                print(e)
                continue

            sentence_outputs.append(y)#* self.output_importance[word[1]])

        return self.output_to_word[np.argmax(np.sum(np.array(sentence_outputs), axis=0))]

    def classify_data(self, x, means, cov):
        y_outputs = []
        for k in range(means.shape[0]):
            y = multivariate_normal.pdf(x, mean=means[k], cov=cov[k], allow_singular=True)
            y_outputs.append(y) # * self.output_probs[self.output_to_word[np.argmax(y)]])

        print("Possibly {}".format(self.output_to_word[np.argmax(y_outputs)]))
        return y_outputs

    def create_model(self):
        mapping = load_UMLS()
        self.train(mapping)
        print(self.predict("I can't sleep and I am exhausted, nausea"))
        print(self.get_questions())

    def get_questions(self):
        best_guesses = []
        guesses = []

        for k in range(self.covariances.shape[0]):
            w, v = np.linalg.eig(self.covariances[k])
            index = np.argmax(w)

            vec = self.gram_smidt(v[:, index].real, self.total_data)
            if vec[0] < 0.96:
                best_guesses.append((self.cos_sim(vec, self.encoder.get_vector("symptom")), self.encoder.similar_by_vector(vec, topn=1)))

        top_indices = sorted(best_guesses)[len(best_guesses) - self.MAX_QUESTIONS:]

        for t in top_indices:
            guesses.append(t[1][0][0])

        return guesses

    def cos_sim(self, v1, v2):
        return np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)


    def gram_smidt(self, new_vec, prev_vectors):
        for v in prev_vectors:
            new_vec -= self.smoothing_factor * (np.dot(new_vec, v) / np.dot(v,v)) * v

        new_vec /= np.linalg.norm(new_vec)

        return new_vec

'''
Way this works:
1) it takes in the initial setup for symptoms->illnesses. This can come in any general format and can get updated frequently
2) it uses entropy calculations to decide which words are to be considered 'keywords' and then parses thm out from the sentence
3) It then vectorizes each of those words using Word2Vec so that synonyms are mapped to very similar points in space
4) This is used to train a multivariate guassian distribution with multiple covariances matrices for each output class.
    a) We normalize the covariance a bit to ensure that the data doesn't end up with ridiculous values, even with very low amounts of data
5) We then wait for a sentence to come in and then classify each symptom based on its gaussian distribution of that word
    a) We combine the distibutions using the priors taken from the data to get a general assessment for the illness at hand
6) Whenever we get doctor data, we simply add it to the dataset and recalculate the mean and covariance matrices, which is essentially instant
7) Whenever we get a call for it, we can also suggest certain key words for what to ask the patient
    a) calculates where the most additional information is found by analyzing the eigenvalues of the covariance matrices using PCA analysis
    b) It then maps this 'desired' information to healthcare data using word2vec mappings
    c) It then uses gram_smidt orthogonal mapping to change its predictions/questions it asks dynamically 
'''
if __name__ == "__main__":
    m = MVG()
    m.create_model()
