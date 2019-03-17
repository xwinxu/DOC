import os
import pickle
import sys

SAVED_DATA_PATH = "data/saved.pkl"

def load_UMLS():
    diseases = {}

    g = open("data/data.txt", 'r')
    f = g.read().replace("\n\n\n\n\n\n\n\n", 'SYMP=').replace("\n\n\n", '_____').split('\n')
    g.close()

    for line in f:
        if line == '':
            continue

        disease = line.split("_____")[0].split('_')[-1].split("^")[0]
        diseases[disease] = {'count': int(line.split("_____")[1]), "symptoms": []}

        diseases[disease]['symptoms'] = [[]]
        diseases[disease]['symptoms'][0] += line.split("_____")[-1].split("SYMP=")[0].split("_")[-1].split(' ')

        symptoms = line.split("SYMP=")[1:]

        for s in symptoms:
            diseases[disease]['symptoms'][0] += s.split("_")[-1].split("^")[0].split(' ')

    return diseases

def load_all():
    saved_data = {}
    basis = load_UMLS()

    if os.path.isfile(SAVED_DATA_PATH):
        saved_data = pickle.load(open(SAVED_DATA_PATH, 'rb'))
    else:
        pickle.dump(saved_data, open(SAVED_DATA_PATH, 'wb'))

    for key, item in saved_data:
        val = basis.get(key, {'count': 500, "symptoms": []})
        for s in item['symptoms']:
            val['symptoms'].append(s)

        basis[key] = val

    return basis


if __name__ == "__main__":
    print(load_all())
