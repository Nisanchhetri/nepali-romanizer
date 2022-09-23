import nltk
import multiprocessing
from collections import Counter
from nltk import timeit
from fig2word import expandText
import numpy as np
import re
import os

text = open('scraped/readBook.txt', mode='r', encoding='utf8').read().split('\n')
a = list(nltk.ngram(text[0]))
g = nltk.ngram_gen(text[0])
g = (list(g))
print(a)
print(g)

# words = nltk.wordTokenizer(text)
# words = sorted(set(words))
# with open('vocab.csv', mode='w', encoding='utf8') as file:
#     file.write('\n'.join(words))
