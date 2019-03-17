def load_UMLS():
    diseases = {}
    g = open("data.txt", 'r')
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


if __name__ == "__main__":
    print(load_UMLS())
