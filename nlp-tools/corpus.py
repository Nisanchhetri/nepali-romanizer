# !/usr/bin/python
# -*- coding=utf-8 -*-

from nltk import timeit
from collections import Counter
import os
import nltk
from fig2word import expandText

ENCODING = 'utf8'


@timeit
def corpusComposition(input_filename='scraped/corpus.csv'):
    """
    Statistical composition of corpus.
    Check: This module can have vars of large size.
    Make sure to delete it once it goes out of context.
    """
    # Read corpus and tokenize it into words
    corpus = open(input_filename, encoding=ENCODING, mode='r').read()
    print('No of characters in corpus : {}'.format(len(corpus)))

    words = nltk.wordTokenizer(corpus)
    print('Corpus size : {}'.format(len(words)))

    average_length = len(corpus) / len(words)
    print('Average word length :  %.2f' % average_length)
    del corpus

    print('Initial vocab size : {} '.format(len(set(words))))

    # Lemmatize
    lemmatizer = nltk.lemmatizer() # init lemmatizer
    words = lemmatizer.lemmatizeList(words) # lemmatizes list in an efficient manner using dict
    print('Lemmatized vocab size : {}'.format(len(set(words))))
    del lemmatizer

    # Count the occurence of each word and sort it in the order of decreasing word count
    word_counters = Counter(words)
    word_counters = sorted(word_counters.items(), key=lambda x: x[1], reverse=True)

    corpus_size = len(words)
    del words

    percentCount, numberCount = 0, 0
    eightyMilestone, ninetyMilestone = False, False
    for index, [key, value] in enumerate(word_counters):
        numberCount += value
        percentCount = numberCount / corpus_size

        # Size of top 100 words
        if index == 99:
            print('Top 1000 words make {} words or {} of the corpus'.format(numberCount, (numberCount / corpus_size)))

        # Size of top 1000 words
        if index == 999:
            print('Top 1000 words make {} words or {} of the corpus'.format(numberCount, (numberCount / corpus_size)))

        # 80% of vocab is contained in how many words
        if not eightyMilestone:
            if percentCount >= 0.80:
                print('{} words make {}% of the corpus'.format(index + 1, percentCount))
                eightyMilestone = True

        # 90% of vocab is contained in how many words
        if not ninetyMilestone:
            if percentCount >= 0.90:
                print('{} words make {}% of the corpus'.format(index + 1, percentCount))
                ninetyMilestone = True

        # 99% of vocab is contained in how many words
        if percentCount >= 0.99:
            print('{} words make {}% of the corpus'.format(index + 1, percentCount))
            break


def convertToReadingFormat(input_filename='scraped/ekantipur.csv', output_dir='./scraped'):
    """
    Tokenize the corpus into sentence.
    Expand numbers.
    Remove sentences with typos
    Write sentences to file
    """

    SENT_LENGTH_THRESH = 150

    # Assuring that both input file exists and output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    assert os.path.exists(input_filename) == True
    # assert os.path.exists(os.path.dirname(output_filename)) == True

    print('1/3 Reading Corpus')
    corpus = open(input_filename, mode='r', encoding='utf8').read()
    corpus = nltk.cleantext(corpus)

    # Expand figure to words : 1 -> one
    corpus = expandText(corpus)

    print('2/3 Tokenizing Corpus')
    corpus = nltk.sentTokenizer(corpus)  # returns sentence tokenized corpus
    print('3/3 Writing Output')
    print('Sentences found : ', len(corpus))
    output_filename = os.path.join(output_dir, 're_' + os.path.basename(input_filename))

    with open(output_filename, mode='w', encoding='utf8') as tokenizedCorpusFile:
        for sentence in corpus:
            sentence = nltk.sentenceWithoutTypo(text=sentence)
            if len(sentence) < SENT_LENGTH_THRESH:
                tokenizedCorpusFile.write(sentence + '\n')

    del corpus


@timeit
def makeCorpus(inputPath, outputFilename='corpus.txt'):
    """
    Takes a dir as input.
     Reads text from all the text files in that directory
        Clean
     Writes all the text into outputFilename

    Output filename is automatically generated.
    """

    # Check if the inputPath exists
    if not os.path.exists(inputPath):
        print("The path doesn't exist. Breaking")
        assert os.path.exists(inputPath) == True

    # Folders inside the dir corresponding to different sources
    dirs = os.listdir(inputPath)
    dirs = [path for path in dirs if "." not in path]
    print('Dirs : ', dirs)

    corpusFile = open("corpus.csv", mode='w', encoding='utf8')
    for dir in dirs:

        files = os.listdir(os.path.join(inputPath, dir))
        print('Processing {} directory with {} files'.format(dir, len(files)))

        # Save files in entire directory into a text file # Directory wise corpus
        # kantipur.csv
        dirfilename = os.path.join('scraped', dir) + ".csv"
        dirfile = open(dirfilename, encoding='utf8', mode='w')
        assert os.path.exists(dirfilename) == True

        allText = ''
        for filename in files:
            # Generate complete filename
            filename = os.path.join(os.path.join(inputPath, dir), filename)

            # Read the file which is presumably of small size
            text = open(filename, encoding='utf-8', mode='r').read()

            # If the text is not empty or some jibberish, write it to file
            if len(text) > 20:
                # Clean text
                text = nltk.cleantext(text)
                allText += text

        # Write all the text at once to file
        corpusFile.write(text)  # total corpus
        dirfile.write(text)  # dir corpus
        dirfile.close()  # close the individual file

        # Get the word count
        words = nltk.wordTokenizer(text)
        print('Corpus size of {} : {} '.format(dir, len(words)))
        print('Vocab size of {} : {} '.format(dir, len(set(words))))

    corpusFile.close()


@timeit
def makeCorpusFromDir(inputPath, SHOW_PROGRESS_STEP=1000):
    """
    Takes a dir as input and writes all the text in that dir to dirname.csv
    XML-->UTF16
    """

    # Check if the inputPath exists
    if not os.path.exists(inputPath):
        print("The path doesn't exist. Breaking")
        assert os.path.exists(inputPath) == True

    # Output filename : path + .csv
    outputFilename = os.path.dirname(inputPath) + '.csv'

    allText = ''
    import glob
    files = glob.glob(os.path.join(inputPath, '*.*'))
    corpusFile = open(outputFilename, mode='w', encoding='utf8')

    # print(files)
    for index, filename in enumerate(files):

        if index % SHOW_PROGRESS_STEP == 0:
            print('Processing {} / {} : {}'.format(index, len(files), filename))

        # Read the file which is presumably of small size
        text = open(filename, encoding='utf8', mode='r').read()

        # If the text is not empty or some jibberish, write it to file
        if len(text) > 20:
            # Clean text
            text = nltk.cleantext(text)
            allText += text

    # Write all the text at once to file and close it.
    # In some cases writing all collected text at once might be impractical.
    corpusFile.write(allText)  # total corpus
    corpusFile.close()

    # Get the word count
    words = nltk.wordTokenizer(allText)
    print('Corpus size of {} : {} '.format(outputFilename, len(words)))
    print('Vocab size of {} : {} '.format(outputFilename, len(set(words))))


def addCorpus(input_dir='./scraped', format='.csv', output_filename='./scraped/corpus.csv'):
    """
    :param input_dir: Directory containing the individual corpuses
    :param format: .txt, .csv - format of corpuses
    :param output_filename:
    :return:
    """
    import glob
    # Find all files of specific format in the input_dir
    files = glob.glob(os.path.join(input_dir, '*' + format))
    files = sorted(files)

    # Read each corpus one by one and add to the main corpus
    with open(output_filename, encoding='utf8', mode='w') as output_file:
        for index, filename in enumerate(files):
            try:
                print('Processing {} / {} : {}'.format(index, len(files), filename))
                text = open(filename, mode='r', encoding='utf8').read()
                output_file.write(text)
            except:
                print(filename, '*' * 20)


def bestSentenceForSynthesis(input_filename='./scraped/poem.csv', MIN_LEN=60, MAX_LEN=100, LANG='NP', VOCAB=0.6,
                             output_filename='scraped/readBook.txt'):
    """
    Cleans script. Tokenize into sentence.
    Compute score for each sentence
    """
    import numpy as np
    from bisect import bisect_right
    correctedVocab = open('./dict/vocab-corrected.csv', mode='r', encoding='utf8').read().split('\n')

    if LANG == "NP":
        no_of_letters = 93  # for Nepali
    else:
        no_of_letters = 40  # for English

    if not os.path.exists(input_filename):
        print("The input directory doesn't exist")
    assert os.path.exists(input_filename)

    # Read text from file and convert it into list of characters
    text = open(input_filename, mode='r', encoding='utf8').read()
    sentences = nltk.sentTokenizer(text)
    vocab = nltk.wordTokenizer(text)
    vocab = Counter(vocab).most_common(int(len(set(vocab)) * VOCAB))
    vocab = [word for word, count in vocab]
    vocab = sorted(vocab)
    print('Total sentences : {}'.format(len(sentences)))
    print('Length of {} vocabulary :{}'.format(VOCAB, len(vocab)))

    # Zeros for padding
    zeros = np.zeros((no_of_letters), np.int32)
    zeros = list(zeros)

    # Filter out sentences having more than average standard deviation
    dict_sentences = {}
    for index, sentence in enumerate(sentences):
        try:
            # Display progress
            STEP = 10000
            if index % STEP == 0:
                print("Processing {} 10k / {}".format(index // STEP, len(sentences) // STEP))

            # We only wants sentences with length greater than min_len and less than max_len
            if len(sentence) > MAX_LEN or len(sentence) < MIN_LEN:
                # print('Rejected : ', sentence)
                continue

            # Remove sentences whose words are not in vocab or if the words are too long
            sentence = sentence.strip('\n')
            sentence = nltk.remove_punct(sentence)
            words = nltk.wordTokenizer(sentence)  # tokenize into words
            for word in words:
                # If the word is too long
                if len(word) > 11:
                    # print('Rejected : ', word, vocab_word)
                    break

                # if the word is not among popular vocabulary
                vocab_word = vocab[max(0, bisect_right(vocab, word) - 1)]
                correct_vocab_word = correctedVocab[max(0, bisect_right(correctedVocab, word) - 1)]

                if word != correct_vocab_word:
                    break

                if word != vocab_word:
                    break

                # If the word is a typo
                if nltk.isTypo(word):
                    break

                expanded_sentence = expandText(sentence)
                if expanded_sentence != sentence:
                    break

            else:
                # print('Simple sentence : ', sentence)
                # Check if the sentence has right combination of all letters
                chars = list(sentence)  # convert sentence into list
                chars_score = Counter(chars)  # count the occurenence of letters
                counts = [value for key, value in chars_score.items()]  # take the counts
                counts = counts + zeros[
                                  :no_of_letters - len(counts)]  # put zeros for all the characters that weren't found
                score = np.std(counts)  # Std dev of character count, lesser the better

                # score = len(set(list(sentence))) / len(sentence)
                dict_sentences.update({sentence: score})
        except:
            # Word not in vocab
            # print('Discarded : ', sentence)
            pass

    dict_sentences = sorted(dict_sentences.items(), key=lambda x: x[1], reverse=False)  # sort according to std dev

    average_std = np.average([score for key, score in dict_sentences])
    sentences = [sentence for sentence, score in dict_sentences if score < 1.5 * average_std]
    print('Average std dev : {}'.format(average_std))
    print('Discarded {} sentence after removing sentence with high stddev. \nTotal remaining sentences : {}'.format(
        len(dict_sentences) - len(sentences), len(dict_sentences)))
    print('Total simple sentences : ', len(dict_sentences))

    with open(output_filename, mode='w', encoding='utf8') as file:
        for sentence, score in dict_sentences:
            file.write("{}\n".format(sentence))


if __name__ == "__main__":
    # tokenizeCorpus()
    # generateScriptForRecording('C:/Users/paaila\Documents\PycharmProjects\Tools\original')
    # generateScriptForRecording('C:/Users/paaila\Documents\PycharmProjects\Python-Audio-Crop-nepali-tokenizer\Data\Audio')
    # input_filename = '../QA/Data/basetext.txt'

    # addCorpus(input_dir='text', format='.txt', output_filename='text/constitution2127.csv')
    input_filename = 'scraped/book.csv'
    # makeCorpusFromDir(inputPath='book')
    bestSentenceForSynthesis(input_filename=input_filename, output_filename='scraped/readBook2.txt')

    # convertToReadingFormat(input_filename='scraped/readtext.txt')
    pass
