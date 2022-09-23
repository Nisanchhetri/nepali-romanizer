import os
import nltk
from collections import Counter
from bisect import bisect_right
from nltk import timeit
import fig2word

ENCODING = 'UTF8'

__all__ = ['cleanMPPDictionary', 'processDictionary', 'usedWordsFromMPP', 'newWordsFromCorpus', 'dictionaryFromCorpus']


def cleanMPPDictionary():
    """
    Take only words from the MPP base dictionary: ne_NP.dic
    Clean MPP dictionary
    """
    filename = 'ne_NP.dic'
    assert os.path.exists(filename) == True
    print('{} :" {} '.format(filename, os.path.exists(filename)))

    # Clean MPP dict
    dict = open(filename, encoding='utf8', mode='r').read()
    import nltk

    dict = nltk.cleantext(dict)  # remove all things that do not belong to the list of nepali alphabet characters
    dict = dict.split(' ')  # separate text into words

    # write words to file
    file = open('dict.csv', mode='w', encoding='utf8')
    for word in dict:
        file.write(word + '\n')
    file.close()  # close file


def processDictionary():
    """
    # Create a word only dictionary and word and index dictionary from MPP expanded dictionary.
    # This is used for lemmatizing
    """

    # Dictionary filenames
    filename = 'dict/ne_NP_unmunched_withid.txt'
    word_only_dict = 'dict/word_only.txt'
    word_and_index_dict = 'dict/dictionary.csv'

    # Open file for writing
    dict_file = open(word_and_index_dict, encoding=ENCODING, mode='w')
    word_only_file = open(word_only_dict, encoding=ENCODING, mode='w')

    # Read the existing MPP dictionary
    dictionary = open(filename, mode='r', encoding='utf8').readlines()
    # dictionary = (dictionary[44902:])
    print('Length of dictionary : ', len(dictionary))

    # MPP expanded dictionary contains both word and their index in the base dictionary (with 36k word count)
    for wordAndIndex in dictionary:
        _, _, word = wordAndIndex.split('|')
        word = nltk.cleanword(word)
        word_only_file.write(word + '\n')
        dict_file.write(wordAndIndex)

    # Close file after reading
    dict_file.close()
    word_only_file.close()


def usedWordsFromMPP(corpus_filename='scraped/corpus.csv'):
    """ Finds words in MPP expanded dictionary which are actually used. """
    corpus = open(corpus_filename, mode='r', encoding='utf8').read()

    wordsinCorpus = nltk.wordTokenizer(corpus)
    del corpus
    wordsinCorpus = set(wordsinCorpus)

    # Lemmatize and stemming
    lemmatizer = nltk.lemmatizer()
    # stemmer = nltk.stemmer()

    wordsinCorpus = [lemmatizer.lemmatize(word) for word in wordsinCorpus]
    wordsinCorpus = sorted(set(wordsinCorpus))

    print('Corpus size after lemmatizing and stemming : {} '.format(len(wordsinCorpus)))
    # del stemmer
    del lemmatizer

    # Read words from dictionary
    dictionary = open('dict/ne_NP_unmunched_withid.txt', mode='r', encoding='utf8').read().split('\n')
    usefulWord = []
    for index, wordandIndex in enumerate(dictionary):
        try:
            pre, line, word = wordandIndex.split('|')
            reconstruct = word + '|' + line + '|' + pre
        except:
            print('Word : ', wordandIndex, index)
            continue

        pos = bisect_right(wordsinCorpus, word)
        if wordsinCorpus[pos - 1] == word:
            # word in dictionary exists in corpus
            usefulWord.append(reconstruct)

    print('Only {} useful words found in dictionary'.format(len(usefulWord)))
    with open('dict/usefulword.csv', mode='w', encoding='utf8') as file:
        for word in usefulWord:
            file.write(word + '\n')

    return usefulWord


@timeit
def newWordsFromCorpus(input_corpus_name='scraped/corpus.csv', output_filename='dict/newWordsFromCorpus.csv'):
    """
    Find new words that has to be added to the dictionary
    Algorithm:
        Lemmatize the word
        Check if it exists in dictionary and stem it
        If it doesn't, it's a new word that needs to be considered for appending to dictionary
    Words from the most common 1 lakh words are only considered as potential candidate
    """

    corpusText = open(input_corpus_name, mode='r', encoding=ENCODING).read()
    allwords = nltk.wordTokenizer(corpusText)
    del corpusText

    print('Corpus size : {}'.format(len(allwords)))
    print('Vocabulary size : {}'.format(len(set(allwords))))

    MOST_COMMON_WORDS = int(0.5 * len(set(allwords)))
    MOST_COMMON_WORDS = 150000

    # Count words to find the MOST_COMMON_WORDS
    word_count = Counter(allwords)
    word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    # Keep the MOST_COMMON_WORDS
    allwords = []
    common_words = open('commonwords.csv', mode='w', encoding='utf8')
    for count, [key, value] in enumerate(word_count):
        allwords.append(key)
        common_words.write(key + '|' + str(value) + '\n')
        if count == MOST_COMMON_WORDS:
            common_words.close()
            break

    del word_count

    # lemmatize all the words and sort
    lemmatizer = nltk.lemmatizer()

    allwords = [lemmatizer.lemmatize(word) for word in set(allwords)]

    print('Lemmatized Vocabulary size : {}'.format(len(set(allwords))))
    del lemmatizer

    DISPLAY_LOG_STEPS = 20000
    word_only_dictionary = open('dict/word_only.txt', mode='r', encoding=ENCODING).read().split('\n')

    # If words are not present in dictionary, they are new words
    new_word, old_word = [], []
    for index, word in enumerate(allwords):
        pos = bisect_right(word_only_dictionary, word)
        if word_only_dictionary[pos - 1] == word:
            # word found from old dictionary. yeyy
            old_word.append(word)
            pass
        else:
            # new word found
            new_word.append(word)

        # Display progress
        if index % DISPLAY_LOG_STEPS == 0:
            print('\nProcessing {} / {} words '.format(index, len(allwords)))
            print('New words : {} Old Words : {}'.format(len(new_word), index + 1 - len(new_word)))

    del allwords

    # Write new words to file
    print('\nTotal discovered new words size: {} '.format(len(new_word)))

    with open(output_filename, mode='w', encoding=ENCODING) as new_word_file:
        for word in new_word:
            new_word_file.write(word + '\n')

    old_word = sorted(set(old_word))
    with open('dict/oldwords.csv', mode='w', encoding=ENCODING) as old_word_file:
        for word in old_word:
            old_word_file.write(word + '\n')

    del new_word, old_word


@timeit
def dictionaryFromCorpus(input_filename='./scraped/corpus.csv', output_filename='dict/paaila_dict.csv',
                         top_percent=0.9):
    """
    find the top_percent vocabulary of the corpus
    :param top_percent: [0-1]
    :return:
    """
    print('1/4 Reading corpus')
    words = open(input_filename, mode='r', encoding='utf8').read()
    print('1.2/4 Tokenizing words')
    words = nltk.wordTokenizer(words)  # cleans text and tokenizes it into words
    print('1.3/4 Expanding words')
    words = [fig2word.updateText_test(word) for word in words]
    corpus_size = len(words)
    print('Corpus size: {} '.format(corpus_size))
    print('Vocab size : {} '.format(len(set(words))))

    print('2/4 Lemmatizing words in corpus')
    # Lemmatizing words in corpus
    lemmatizer = nltk.lemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    with open('./scraped/lemmatized_corpus.csv', mode='w', encoding='utf8') as file:
        file.write(' '.join(words))

    words_count = Counter(words)
    del words, lemmatizer

    words_count = sorted(words_count.items(), key=lambda x: x[1], reverse=True)

    print('3/4 Taking the {} mose valuable words'.format(top_percent))
    # Take the top_percent words only
    useful_words = dict()
    word_count = 0
    for key, value in words_count:
        word_count += value
        # If we haven't reached the threshold, append words
        if word_count / corpus_size < top_percent:
            useful_words[key] = value

    print('4/4 Writing results to the file.')
    # Write result to output_filename
    with open(output_filename, mode='w', encoding='utf8')  as file:
        useful_words = sorted(useful_words.items(), key=lambda x: x[1], reverse=True)
        for word, count in useful_words:
            # If the word is not a typo
            if not nltk.isTypo(word):
                file.write('{} \t {}\n'.format(word, str(count)))

    print('Vocab size : {}'.format(len(useful_words)))


def getDictionaryFast(input_filename='./scraped/corpus.csv', top_k=10000, output_filename='paaila_dict.csv'):
    # Read the corpus and tokenize it into words
    words = open(input_filename, mode='r', encoding='utf8').read()
    words = nltk.wordTokenizer(words)
    print('Corpus size : {}'.format(len(words)))
    print('Vocabulary size : {}'.format(len(set(words))))

    # Find the suffix of all the words
    lemmatizer = nltk.lemmatizer()
    word_count = Counter(words)
    lemmatized_vocab = Counter()

    vocab = list(set(words))
    del words
    lemmatized_words = [lemmatizer.lemmatize(word) for word in vocab]
    for index, word in enumerate(lemmatized_words):
        lemmatized_vocab.update({word: word_count[vocab[index]]})

    # print(suffix_count)
    del lemmatizer, word_count, lemmatized_words
    lemmatized_vocab = sorted(lemmatized_vocab.items(), key=lambda x: x[1], reverse=True)

    print('Lemmatized vocab : {} '.format(len(set(lemmatized_vocab))))
    del vocab

    # Write the suffix to the output_file
    with open(output_filename, mode='w', encoding='utf8') as file:
        for word, count in lemmatized_vocab:
            # print(key, value)
            file.write('{} | {}\n'.format(word, str(count)))
            pass


if __name__ == "__main__":
    # dictionaryFromCorpus(input_filename='./scraped/corpus.csv')
    # getDictionaryFast(input_filename='pagalbasti.txt', top_k=10000)
    getDictionaryFast()
    pass
