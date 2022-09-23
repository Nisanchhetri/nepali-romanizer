# !/usr/bin/python
# -*- coding=utf-8 -*-
# Nepali NLTK substitute '

import re
import time
from bisect import bisect_right

ENCODING = 'UTF8'

__all__ = ['timeit', 'ngram', 'cleantext', 'cleanword', 'wordTokenizer', 'sentTokenizer', 'lemmatizer', 'stemmer',
           'isTypo', 'sentenceWithoutTypo', 'remove_punct']


# text cleaning is the most expensive function here.
# think of ways to make it quicker

def timeit(method):
    """
    A decorator used for time profiling functions and methods
    :param method:
    :return: time in ms for a method
    """

    def timed(*args, **kwargs):
        timeStart = time.time()
        result = method(*args, **kwargs)
        timeEnd = time.time()

        if 'log_time' in kwargs:
            name = kwargs.get('log_name', method.__name__.upper())
            kwargs['log_time'][name] = int((timeEnd - timeStart) * 1000)
        else:
            print('%r %2.2f ms' % (method.__name__, (timeEnd - timeStart) * 1000))
        return result

    return timed


@timeit
def ngram(text, n=2):
    """ Accepts string and returns ngram
    Args:
        text: the text of whose ngram is to be computed
        n: 1 for unigram, 2 for bigram and so on
    Returns:
        generator of ngrams
    """
    # return [text[i:i + n] for i in range(len(text)-1)][:-1]
    return (text[i:i + n] for i in range(len(text) - 2))


def remove_punct(sentence):
    """
    Replaces certain certain with other characters to better aid spell error detection.
    Args:
        sentence: string where character subsitution and replacement is to be performed
    Returns:
        string with substituted characters
    """
    sentence = sentence.replace("ऎ", "ऐ")

    sentence = sentence.replace("ऑ", "औ")

    sentence = sentence.replace("ऒ", "ओ")
    sentence = sentence.replace("ॠ", "ऋ")
    sentence = sentence.replace("ऩ", "न")
    sentence = sentence.replace("ऱ", "र")
    sentence = sentence.replace("ळ", "ल")
    sentence = sentence.replace("़", "")
    sentence = sentence.replace("ॅ", "ँ")
    sentence = sentence.replace("ॆ", "े")
    sentence = sentence.replace("ॉ", "ौ")
    sentence = sentence.replace("ॊ", "ो")
    sentence = sentence.replace("॔", "")
    sentence = sentence.replace("ॐ", "ओम")
    sentence = sentence.replace("ख़", "ख")
    sentence = sentence.replace("ज़", "ज")
    sentence = sentence.replace("ड़", "ड")
    sentence = sentence.replace("ढ़", "ढ")
    sentence = sentence.replace("फ़", "फ")

    sentence = sentence.strip()
    return sentence


@timeit
def sentTokenizer(text):
    """
    Takes string as input and returns list of sentence.
    It doesn't clean text.

    Algorithm:
        Find delimiters.
        Sentence is text from beginning to that de-limiter. Iterate.

    What is a sentence?
        A sentence should have its' delimiter
            Every sentence must end with a question mark, or quote or exclamation. or | or ||
    """

    pos = re.finditer('[।"|?॥]', text) # find all the occurences of the delimiter

    start = 0
    sentTokens = []
    for item in pos:
        end = item.end()
        sentence = text[start:end]
        # If the first char is space, remove it.
        if sentence[0] == ' ':
            sentence = sentence[1:]
        sentTokens.append(sentence)
        start = end

    return sentTokens


# @timeit
def wordTokenizer(text):
    """
    Takes a corpus of text and returns list of words

    ALGORITHM:
        Take string as input
        Discard characters out of range of nepali characters
        Split by space

    Letter range : 0900-\u097F
    Vowel range:
    Number range:
    """

    # Find words, questions, exclaimation and purna biram
    text = re.sub('[^\u0900-\u097F\s]|।', '', text)
    text = text.split()
    return text


def test_wordTokenizer():
    'Test for wordTokenizer'

    # Read text and tokenize it
    text = open('./test/token_input.txt', encoding='utf-8').read()
    wordTokens = wordTokenizer(text)

    # Read expected word tokens and clean first word token
    truth_word_tokens = open('./test/token_groundtruth.txt', encoding='utf-8').read().split('\n')
    truth_word_tokens[0] = cleanword(truth_word_tokens[0])

    with open('testoutput_tokenizer.txt', encoding='utf8', mode='w') as file:
        file.write('\n'.join(wordTokens))

    print('Base truth tokens:', len(truth_word_tokens), '\tObtained tokens: ', len(wordTokens))

    assert wordTokens == truth_word_tokens
    print('Word token is wokring perfectly.')


# @timeit
def cleantext(text):
    """
        Returns only devanagari chars and delimiters.

        There are two ways to clean text.
        1. Remove unwanted characters and the remaining is clean text.
        2. Take only the characters from desired range.
        This algorithm uses the first approach

        punctuations = '\,|\"|\'| \)|\(|\)| \{| \}| \[| \]| \:-|/|\—'

        Note: Compiled regex and compile on the fly regex do not have significant differences.
    """

    # Find words, questions, exclaimation and purna biram
    text = re.sub('[^\u0900-\u097F\?\!\s\॥]', '', text)
    text = text.split()  # removes all whitespace characters including new lines \n, tabs \t, form feeds, return
    text = ' '.join(text)
    return text


def cleanword(text):
    """ Returns only devanagari chars and sentence and word delimiters. """

    nepchars = re.findall('[\u0900-\u097F]', text)
    word = ' '.join(nepchars)
    return word


class lemmatizer:
    """
    Made a class so that lemmatizer won't have to keep reading suffixes from file every time lemmatizer is called.
    Difference between lemmatizer and stemmer in this implementation is this lemmatizer removes only last layer of
    preposition while stemmer tries to return the base/root word
    """

    def __init__(self):
        # filename = "II_new.csv"
        filename = "dict/usefulPrep.csv"
        self.donot_lemmatize = open('dict/donot_lemmatize.csv', mode='r', encoding='utf8').read().split('\n')
        self.suffix = open(filename, encoding='utf8', mode='r').read().split('\n')

    def lemmatize(self, word):
        """
        Remove inflections caused by preposition

        It's not worth checking the length of the word before deciding if it should be lemmatized because most words
        satisfy the criteria. So it is just hindrance to them for the sake of few words which should be lemmatized

        :return suffix stripped word if there was any suffix in the word
        """

        #  Check if the word should be lemmatized or not
        pos = bisect_right(self.donot_lemmatize, word)
        if self.donot_lemmatize[max(pos - 1, 0)] == word:
            # print('Do not lemmatize : ', word)
            return word

        for suff in self.suffix:
            if word[-len(suff):] == suff:
                word = word[:-len(suff)]
                break
        return word

    @timeit
    def lemmatizeList(self, words=None):
        """
            Suitable for lemmatizing whole corpus.
            If you want to lemmatize single word use lemmatize module
        """
        words_set = set(words)  # Find the set of words to lemmatize
        lemmatize_dict = {}  # Store word and their lemmatized version
        # Lemmatize words and store it in dict
        for word in words_set:
            lemmatize_dict[word] = self.lemmatize(word)
        lemmatized = [lemmatize_dict[word] for word in words]
        del words_set, lemmatize_dict
        return lemmatized

    def wordAndPrep(self, word):
        """
        :return word, suffix
        """
        for suff in self.suffix[1:]:
            if word[-len(suff):] == suff:
                word = word[:-len(suff)]
                break
        else:  # If the loop ran without breaking or without finding any preposition
            suff = ''
        return word, suff

    def findSuffix(self, word):
        """
        :return suffix
        """

        try:

            for suff in self.suffix[1:]:
                if word[-len(suff):] == suff:
                    return suff
                    # break
            else:  # If the loop ran without breaking or without finding any preposition
                suff = ''
        except:
            print('Word received : ', word)
        return suff

    @timeit
    def test_lemmatizer(self):
        """
        Test the lemmatizer to see if it is working
        A more robust test with input files and base truth using assess would be better
        """
        groundtruth = open("test/lemmatizer_groundtruth.txt", encoding='utf8', mode='r').read().split('\n')
        input = open("test/lemmatizer_input.txt", encoding='utf8', mode='r').read().split('\n')

        # Check if the words in both files are aligned
        initially_lemmatized = 0
        for w1, w2 in zip(groundtruth, input):
            # print(w1,w2, w1 == w2[:len(w1)])
            if w1 == w2:
                initially_lemmatized += 1

        lemmatized = [self.lemmatize(word) for word in input]

        accuracy = 0
        for lemmatized_word, truth in zip(lemmatized, groundtruth):
            if lemmatized_word == truth:
                accuracy += 1
            else:
                print("Input : {}\t Result : {} \tTruth : {}\t".format(input[lemmatized.index(lemmatized_word)],
                                                                       lemmatized_word, truth),
                      lemmatized_word == truth)

        print('Accuracy of lemmatizer : {%.4f} ' % (
            (accuracy - initially_lemmatized) / (len(groundtruth) - initially_lemmatized)))

    @timeit
    def speedtest(self):
        """ Check the improvements caused by using sorted preposition """
        inputwords = open("scraped/corpus.csv", encoding='utf8', mode='r').read()
        inputwords = wordTokenizer(inputwords)
        lemmatizedWords = [self.lemmatize(word) for word in set(inputwords)]


class stemmer:
    """
    Made a class so that lemmatizer won't have to keep reading suffixes from file every time lemmatizer is called.
    Difference between lemmatizer and stemmer in this implementation is this lemmatizer removes only last layer of
    preposition while stemmer tries to return the base/root word
    """

    def __init__(self):
        filename = "dict/stemming.txt"
        self.donot_lemmatize = open('dict/donot_lemmatize.csv', mode='r', encoding='utf8').read().split('\n')
        self.suffix = open(filename, encoding='utf8', mode='r').read().split('\n')

    def stem(self, word):
        """
        Remove inflections caused by preposition

        It's not worth checking the length of the word before deciding if it should be lemmatized because most words
        satisfy the criteria. So it is just hindrance to them for the sake of few words which should be lemmatized

        :return suffix stripped word if there was any suffix in the word
        """

        #  Check if the word should be lemmatized or not
        pos = bisect_right(self.donot_lemmatize, word)
        if self.donot_lemmatize[max(pos - 1, 0)] == word:
            # print('Do not lemmatize : ', word)
            return word

        for suff in self.suffix:
            if word[-len(suff):] == suff:
                word = word[:-len(suff)]
                break
        return word

    def wordAndSuffix(self, word):
        """
        :return word, suffix
        """
        for suff in self.suffix[1:]:
            if word[-len(suff):] == suff:
                word = word[:-len(suff)]
                break
        else:  # If the loop ran without breaking or without finding any preposition
            suff = ''
        return word, suff

    def findSuffix(self, word):
        """
        :return suffix
        """

        try:

            for suff in self.suffix[1:]:
                if word[-len(suff):] == suff:
                    return suff
                    # break
            else:  # If the loop ran without breaking or without finding any preposition
                suff = ''
        except:
            print('Word received : ', word)
        return suff

    @timeit
    def test_stemmer(self):
        """
        Test the lemmatizer to see if it is working
        A more robust test with input files and base truth using assess would be better
        """

        groundtruth = open("test/lemmatizer_groundtruth.txt", encoding='utf8', mode='r').read().split('\n')
        input = open("test/lemmatizer_input.txt", encoding='utf8', mode='r').read().split('\n')

        # Check if the words in both files are aligned
        initially_lemmatized = 0
        for w1, w2 in zip(groundtruth, input):
            # print(w1,w2, w1 == w2[:len(w1)])
            if w1 == w2:
                initially_lemmatized += 1

        lemmatized = [self.stem(word) for word in input]

        accuracy = 0
        for lemmatized_word, truth in zip(lemmatized, groundtruth):
            if lemmatized_word == truth:
                accuracy += 1
            else:
                print("Input : {}\t Result : {} \tTruth : {}\t".format(input[lemmatized.index(lemmatized_word)],
                                                                       lemmatized_word, truth),
                      lemmatized_word == truth)

        print('Accuracy of lemmatizer : {%.4f} ' % (
            (accuracy - initially_lemmatized) / (len(groundtruth) - initially_lemmatized)))

    @timeit
    def speedtest(self):
        """ Check the improvements caused by using sorted preposition """
        inputwords = open("scraped/corpus.csv", encoding='utf8', mode='r').read()
        inputwords = wordTokenizer(inputwords)
        lemmatizedWords = [self.stem(word) for word in set(inputwords)]


def isTypo(word=''):
    """
    Returns true for typos and false otherwise
    Algorith:
        1. Words beginning with vowels are typos
        2. Words with consecutive vowels are typos
    :param word:
    :return:
    Ram: is also error re.
    """
    vowel_symbol = ('ा','ी','ि','ो','ौ','े','ु','ू','ै','्','ँ','ंं','ः','ृ','्','ृ')

    # To find typos in which a vowel symbol comes at the begining of the word
    if word[0] in vowel_symbol:
        # print('Typo : ',word)
        return True

    else:
         #Find typos of type काठमाडँौ
        if re.search('[ँं][\u093e-\u094f]+|[ँं][\u0901-\u0903]+',word):
            return True

        else:
            # Range for sound symbols
            typos = re.findall('([\u093e-\u094f]+|[\u0901-\u0902]+)', word)
            # Typos are those words in which two sound symbols like ी ि  come consecutively
            for symbol in typos:
                if len(symbol) > 1:
                    return True
            return False


# @timeit
def sentenceWithoutTypo(text):
    """
    Returns Sentence without typo
    :param text:
    :return:
    """
    words = text.split()  # get all the words
    words = [word for word in words if not isTypo(word)]  # check if they are typo
    typoFreeSentence = ' '.join(words)  # join words into sentences
    return typoFreeSentence


if __name__ == "__main__":
    text = open('pronunciation_alphabets.txt', mode='r', encoding='utf8').read()
    text = cleantext(text)
    pass
