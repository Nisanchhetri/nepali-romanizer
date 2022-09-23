"""
Spelling checker
Assumptions:
Words that are the top 100000 words are correct.

If a word is not found in dictionary but has correct suffix, assume it is correct.

Right words are right in just one ways.
They can be misspelled in many ways.
As a result, words with high frequency occurence are most probably correct.

Rameshwat - wat - is uncommon
Rameshwar - correct - we have been hearning lots of ishwar - war is common
"""

import nltk
from nltk import timeit, ngram
from collections import Counter
import numpy as np


class spell:
    @timeit
    def __init__(self, THRESH_PROB=0.0000001):
        """
        Build the n-gram dictionary model
        Read corpus. Find the most common 250,000 words.
        Build ngram
        """
        self.THRESH_PROB = THRESH_PROB

        filename = './scraped/corpus.csv'
        # filename = 'teenghumti.txt'
        self.text = open(filename, encoding='utf8', mode='r').read()

        # Construct bigram_prob and count their frequencies
        bigrams = ngram(self.text)
        bigram_count = Counter(bigrams)
        print('Done counting')
        bigram_prob = {}
        for key, value in bigram_count.items():
            bigram_prob[key] = value / (2 * len(self.text) - 1)
            # print(key, "%.4f" %bigram[key])

        self.bigram_prob = bigram_prob
        del bigram_prob

        # self.wordProbability()
        # print('Ready to evaluate words')
        self.findOptimumThresh()
        # self.wordProbability()

    # 9.972035258025514e-06: 0.43707884050920465
    # 2.781333380666195e-05
    # 4.691902921519111e-05

    def isCorrect(self, word, THRESH_PROB=4.691902921519111e-05):
        """ Returns 1 if the word is correct, 0 otherwise"""
        if len(word) > 1:
            bigrams = ngram(word, n=2)
            try:
                # Calculate probability of each bigrams
                probability = [self.bigram_prob[item] for item in bigrams]
                min_probability = min(probability)
                if min_probability < THRESH_PROB:
                    # Find all the typos
                    errors = {}
                    for bi, score in zip(bigrams, probability):
                        if score < THRESH_PROB:
                            errors[bi] = score
                    # print(word, errors)
                    return 0
                else:
                    return 1

            except KeyError:
                return 0  # If a key is not found, it should possibly be the wrong key

        else:
            return 1  # Assume single character letters are correct.

    def wordProbability(self):
        # All the words in this file are incorrect
        self.text = open('test/typos.csv', mode='r', encoding='utf8').read()
        words = nltk.wordTokenizer(text=self.text)
        probability = [self.isCorrect(word) for word in words[:10000]]
        print('Error Rate : {} against truth of 0'.format("%.2f" % (np.mean(probability))))

        # All the words in this file are correct
        self.text = open('test/token_groundtruth.txt', mode='r', encoding='utf8').read()
        words = nltk.wordTokenizer(text=self.text)
        probability = [self.isCorrect(word) for word in words[:1000]]
        print('Error Rate : {} against truth of 1'.format("%.2f" % (np.mean(probability))))

    def findOptimumThresh(self, MAX_ITER=100, DELTA=0.000001):
        """ Search for the optimum value of MIN_THRESH for detecting spelling errors """
        # All the words in this file are incorrect
        self.text = open('test/typos.csv', mode='r', encoding='utf8').read()
        neg_words = nltk.wordTokenizer(text=self.text)

        # All the words in this file are correct
        self.text = open('test/token_groundtruth.txt', mode='r', encoding='utf8').read()
        pos_words = nltk.wordTokenizer(text=self.text)

        MAX_THRESH = 0.0001
        MIN_THRESH = 0.0000001

        learning_rate = 0.0001

        prev_pos_error = 0.5
        prev_neg_error = 0.5

        pos_delta = 0.5
        neg_delta = 0.5

        error_and_thresh = {}
        for i in range(MAX_ITER):
            THRESH_PROB = np.random.uniform(MIN_THRESH, MAX_THRESH)

            print(
                '\nIteration {}/{} : pos delta {} \tneg delta {} \tTHRESH {}'.format(i, MAX_ITER, pos_delta, neg_delta,
                                                                                     THRESH_PROB))
            neg_probability = [self.isCorrect(word, THRESH_PROB=THRESH_PROB) for word in neg_words]
            neg_error_rate = np.mean(neg_probability)
            print('Error Rate : {} against 0'.format("%.2f" % neg_error_rate))

            pos_probability = [self.isCorrect(word) for word in pos_words]
            pos_error_rate = np.mean(pos_probability)
            print('Error Rate : {} against 1'.format("%.2f" % pos_error_rate))

            pos_delta = prev_pos_error - pos_error_rate
            neg_delta = prev_neg_error - neg_error_rate

            pos_error = 1 - pos_error_rate
            neg_error = neg_error_rate

            total_error = pos_error + neg_error
            error_and_thresh[THRESH_PROB] = total_error

            prev_neg_error = neg_error
            prev_pos_error = pos_error

            # THRESH_PROB -= learning_rate * max((neg_error, pos_error))
            # THRESH_PROB /= 1.5

            if abs(pos_delta) < DELTA and abs(neg_delta) < DELTA:
                print(pos_delta, DELTA)
                break

        # for key, error in error_and_thresh.items():
        #     print("{} : {} ".format(key, "%.4f" %error))

        min_thresh = min(error_and_thresh.values())
        min_error = error_and_thresh[min_thresh]
        print("Min : {} : {} ".format(min_thresh, min_error))


if __name__ == "__main__":
    spell()
    pass
