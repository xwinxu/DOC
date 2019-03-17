pip install -r requirements.txt

wget http://nlp.stanford.edu/data/glove.6B.zip
unzip glove.6B.zip

mv glove.6B/* .

python setup.py
