import os
import nltk
import re
import glob
from nltk import timeit
from collections import Counter
from bisect import bisect_right

ENCODING_XML = 'UTF16'

# All functions in this module
__all__ = ['collectPOS', 'wordPOSTagPair', 'prepositionCombinations', 'sortedprepositionCombinations',
           'allSuffixInCorpus', 'splitWords', 'generateNonStemmableWordList']


def wordPOSTagPair(filename):
    """
    Return dict, tags
    dict is a dictionary of word, postag pair from input XML file
    """

    file = open(filename, encoding=ENCODING_XML, mode='r').readlines()
    dict = {}
    tags = []
    for line in file[:]:
        if line[:2] == "<w":
            group = (line.split('ctag="')[1:])
            for item in group:
                try:
                    word = nltk.cleanword(item)
                    tag = re.findall('[A-Z]+', item)[0]
                    output = (" {} --- {}".format(word, tag))
                    # print(output)
                    dict[word] = tag
                    tags.append(tag)
                except:
                    # Errors occur if there is no matching word and tag pair that is for untagged words
                    pass

    tags = list(set(tags))
    return dict, tags


def collectPOS(inputPath):
    """
    Make a list of POS by reading tags from XML file and save them in their respective files
    :param inputPath:
    :return:
    """
    if not os.path.exists(inputPath):
        print('The path doesn"t exist. Breaking')

    # Folders inside the dir corresponding to different sources
    files = glob.glob(os.path.join(inputPath, '*.xml'))

    for index, filename in enumerate(files):
        print('Processing : {} / {}'.format(index, len(files)))

        # Obtain tags and word and tag pair
        dict, tags = wordPOSTagPair(filename)

        for tag in tags:
            tag_words = []
            tagfilename = './pos/' + tag + ".csv"
            if os.path.exists(tagfilename):
                tag_words = open(tagfilename, encoding='utf8', mode='r').read().split('\n')
                tagfile = open(tagfilename, encoding='utf8', mode='w')
            else:
                tagfile = open(tagfilename, encoding='utf8', mode='w')

            for key, value in dict.items():
                if value == tag:
                    tag_words.append(key)

            # Sort tag words and write them to file
            tag_words = sorted(set(tag_words))
            tagfile.write('\n'.join(tag_words))
            tagfile.close()


def prepositionCombinations(output_filename='II.csv'):
    """
    Make combination of preposition to make comphrensive list of preposition
    :return:

    IH -> IE IKM II IA IKD
    II -> IKF IKM
    """

    # List all preposition filenames
    dir = 'pos'
    suffixFilenames = 'IE.csv IKM.csv II.csv IA.csv IKO.csv'
    suffixFilenames = suffixFilenames.split()
    suffixFilenames = [os.path.join(dir, file) for file in suffixFilenames]
    prefixFile = './pos/IH.csv'

    print(suffixFilenames)

    # Prefix preposition - the preposition that precedes all.
    prefix = open(prefixFile, mode='r', encoding='utf8').read().split('\n')

    # A list to contain all preposition
    listOfPreposition = prefix

    # Generate Combination of prefix and suffix prepositions
    for filename in suffixFilenames:
        suffixPrep = open(filename, mode='r', encoding='utf8').read().split('\n')
        combination = [prefix[1] + suffix for suffix in suffixPrep[1:] if suffix != ' ']
        combination += [prefix[2] + suffix for suffix in suffixPrep[1:] if suffix != ' ']
        listOfPreposition += suffixPrep + combination

    # sort the preposition based on length so that large combinations get removed
    listOfPreposition = sorted(listOfPreposition, key=lambda x: len(x), reverse=True)

    # write the generated preposition to a file
    with open(output_filename, mode='w', encoding='utf8') as file:
        for preposition in listOfPreposition:
            if len(preposition) > 1:
                file.write(preposition + '\n')

    # print(listOfPreposition)
    print('Generated {} prepositions'.format(len(listOfPreposition)))


def prepositionCombinations_dev(output_filename='II_new.csv'):
    """
    Make combination of preposition to make comphrensive list of preposition
    :return:

    Combinations of prepositions
    IH -> IE IKM II IA IKD
    II -> IKF IKM
    """

    # List all preposition filenames
    dir = 'pos'
    suffixFilenames = 'IKF.csv IKM.csv IE.csv IA.csv IKO.csv II.csv'
    suffixFilenames = suffixFilenames.split()
    suffixFilenames = [os.path.join(dir, file) for file in suffixFilenames]
    prefixFile = ['./pos/IH.csv', './pos/II.csv']

    print('Suffix filenames : ', suffixFilenames)

    # A list to contain all preposition
    listOfPreposition = []

    for index, prefix_filenames in enumerate(prefixFile):
        # Prefix preposition - the preposition that precedes all.
        prefix = open(prefix_filenames, mode='r', encoding='utf8').read().split('\n')
        listOfPreposition += prefix

        # Generate Combination of prefix and suffix prepositions
        for index_sub, filename in enumerate(suffixFilenames):

            # Second prefix file does not need all combinations
            if index > 0 and index_sub > 1:
                print('We do not need all combinations')
                break

            suffixPrep = open(filename, mode='r', encoding='utf8').read().split('\n')

            for pre in prefix[1:]:
                combination = [pre + suffix for suffix in suffixPrep[1:]]
                listOfPreposition += suffixPrep + combination

    # sort the preposition based on length so that large combinations get removed
    listOfPreposition = set(listOfPreposition)
    listOfPreposition = sorted(listOfPreposition, key=lambda x: len(x), reverse=True)

    # write the generated preposition to a file
    with open(output_filename, mode='w', encoding='utf8') as file:
        for preposition in listOfPreposition:
            if len(preposition) > 1:
                file.write(preposition + '\n')

    # print(listOfPreposition)
    print('Generated {} prepositions'.format(len(listOfPreposition)))


def sortedprepositionCombinations(input_filename='suffix_test.csv', output_filename='usefulPrep_new.csv'):
    """
    A sorted preposition list can boost lemmatizing
    Sorted in the order of usage / frequency
    Because lemmatizing quits search as soon as the suffix is found
    :return:
    """

    text = open(input_filename, mode='r', encoding='utf8').read().split('\n')
    prep_count = {}
    for index, line in enumerate(text):
        try:
            word, count = line.split(' | ')
            prep_count[word] = int(count)
        except:
            # Probably last line
            # print("Last line : ", line)
            pass
    prep_count = Counter(prep_count)
    sorted_prep_count = sorted(prep_count.items(), key=lambda x: x[1], reverse=True)

    # List of prepositions
    prep_list = [word for word, count in sorted_prep_count]

    # Prepositions sorted in the most efficient way
    for index, prep in enumerate(prep_list):

        # Sort the variations within preposition : pratiko, sangako
        prep_vars = {}
        for largePrep in prep_list[index + 1:]:
            if largePrep[-len(prep):] == prep:
                # print(prep, largePrep)
                prep_vars[largePrep] = prep_count[largePrep]

        # Sort the variations of prep with respect to popularity and change their order in prep_list
        prep_vars = sorted(prep_vars.items(), key=lambda x: x[1])
        prep_vars = [word for word, count in prep_vars]
        for item in prep_vars:
            prep_list.remove(item)
            prep_list.insert(index, item)

    with open(output_filename, mode='w', encoding='utf8') as sortedPrep:
        sortedPrep.write('\n'.join(prep_list))

    print('{} are useful prepositions '.format(len(prep_list)))


@timeit
def allSuffixInCorpus(input_filename='./scraped/corpus.csv', output_filename='suffix.csv'):
    """
    :param input_filename:
    :return:
    """
    # Read the corpus and tokenize it into words
    words = open(input_filename, mode='r', encoding='utf8').read()
    words = nltk.wordTokenizer(words)
    print('Corpus size : {}'.format(len(words)))

    # Find the suffix of all the words
    lemmatizer = nltk.lemmatizer()

    # If the suffix is not blank space
    suffix = [lemmatizer.findSuffix(word) for word in words if word != '']

    print('{} words are followed by preposition '.format(len(suffix)))
    del words, lemmatizer

    # Write the suffix to the output_file
    with open(output_filename, mode='w', encoding='utf8') as file:
        file.write('\n'.join(suffix))


@timeit
def allSuffixInCorpus_test(input_filename='./scraped/corpus.csv', output_filename='suffix_test.csv'):
    """
    :param input_filename:
    :return:
    """

    # Read the corpus and tokenize it into words
    words = open(input_filename, mode='r', encoding='utf8').read()
    words = nltk.wordTokenizer(words)
    print('Corpus size : {}'.format(len(words)))
    print('Vocabulary size : {}'.format(len(set(words))))

    # Find the suffix of all the words
    lemmatizer = nltk.lemmatizer()
    word_count = Counter(words)
    suffix_count = Counter()

    suffix = [lemmatizer.findSuffix(word) for word, count in word_count.items()]
    words = [word for word, count in word_count.items()]
    for index, suff in enumerate(suffix):
        if suff != '':
            suffix_count.update({suff: word_count[words[index]]})

    # print(suffix_count)
    print('{} words are followed by preposition '.format(len(suffix_count)))
    del words, lemmatizer

    print('We have {} suffix altogether '.format(len(suffix_count)))

    # Write the suffix to the output_file
    with open(output_filename, mode='w', encoding='utf8') as file:
        for key, value in suffix_count.items():
            # print(key, value)
            file.write('{} | {}\n'.format(key, str(value)))
            pass


def splitSentence(sentence=''):
    """
    Takes a txt file, tokenizes words and returns splitted words
    Eg.
        Input : Amale malai maya garnuhuncha
        Output : Ama le ma lai maya garnuhuncha

    Algorithm:
        Get a word.
        See if it has any preposition as suffix.
        If it has preposition as suffix:
            Check if it a simple preposition or combination of preposition
            Return root word + prep1 + prep_k
    """
    sentence = nltk.cleantext(sentence)

    if sentence == '' or sentence == ' ':
        return sentence

    suffix = open('Dict/usefulPrep.csv', mode='r', encoding='utf8').read().split('\n')

    lemmatizer = nltk.lemmatizer()

    word_tokens = nltk.wordTokenizer(sentence)
    expandedSentence = []
    for word in word_tokens:
        word, lemmaSuff = lemmatizer.wordAndPrep(word)
        # expandedSentence += word + ' '
        expandedSentence.append(word)
        if lemmaSuff != '':
            for suff in suffix:
                if lemmaSuff[-len(suff):] == suff and len(lemmaSuff) != len(suff):
                    lemmaSuff = lemmaSuff[:-len(suff)]
                    # expandedSentence += lemmaSuff + ' ' + suff + ' '
                    expandedSentence.append(lemmaSuff)
                    expandedSentence.append(suff)
                    break
            else:
                # expandedSentence += lemmaSuff + ' '
                expandedSentence.append(lemmaSuff)
    delimiter = sentence[len(sentence) - 1]
    if delimiter in ['?', '!', '।']:
        # expandedSentence += delimiter
        expandedSentence.append(delimiter)

    del lemmatizer
    return ' '.join(expandedSentence)


@timeit
def generateNonStemmableWordList(input_filename='./scraped/corpus.csv', output_filename='donot_lemmatize.csv'):
    """
    Algorithm:
        Look for words which upon lemmatizing can't be found in dictionary
    :return:
    """

    # Read text from corpus and tokenize it into words
    text = open(input_filename, mode='r', encoding='utf8').read()
    text = set(nltk.wordTokenizer(text))  # all the words in the corpus

    print('Word count : ', len(text))

    # Read words in dictionary
    dictionary = open('./dict/dict.csv', mode='r', encoding='utf8').read().split('\n')
    dictionary = sorted(dictionary)

    # Look for words that can be lemmatized and that are in dictionary.
    lemmatizer = nltk.lemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in text]

    donot_lemmatize = []
    for word, lemmatized_word in zip(text, lemmatized_words):
        # If the word exists in dictionary
        if dictionary[max(bisect_right(dictionary, word) - 1, 0)] == word:
            # If its' lemmatized version doesn't exist in dictionary
            if dictionary[max(bisect_right(dictionary, lemmatized_word) - 1, 0)] != lemmatized_word:
                # Then it should not be lemmatized
                donot_lemmatize.append(word)

    del lemmatizer
    donot_lemmatize = set(donot_lemmatize)

    # Writing output to the output file
    with open(output_filename, mode='w', encoding='utf8') as file:
        donot_lemmatize = sorted(donot_lemmatize)
        file.write('\n'.join(donot_lemmatize))

    print('Summary : {} / {} should not be lemmatized'.format(len(donot_lemmatize), len(text)))


def tagPOS(input_filename='paaila_dict.csv'):
    """
    Tag words with their respective
    :return:
    """

    # Generate base list of word and pos tag
    pos_dir = './pos'
    pos_files = glob.glob(os.path.join(pos_dir, '*.csv'))
    pos = dict()
    for filename in pos_files:
        tag = os.path.basename(filename).split('.')[0][0] * 2
        wordlist = open(filename, mode='r', encoding='utf8').read().split('\n')
        for word in wordlist:
            pos[word] = tag

    text = open(input_filename, mode='r', encoding='utf8').read()
    text = nltk.wordTokenizer(text)

    print('Vocab size : ', len(text))
    # Tag input words with corresponding Part of Speech
    tagged = dict()
    for index, word in enumerate(text):
        # Display progress

        if len(re.findall('[\u0905-\u0939]', word)) < 2:
            print('Rejected : {}'.format(word))
            continue

        if index % 100 == 0:
            print('Processing {} / {} words'.format(index, len(text)))

        if nltk.isTypo(word):
            continue

        try:
            tagged[word] = pos[word]
            print(word, pos[word])
        except:
            tagged[word] = 'UNK'

    with open('tagged_paaila_dict.csv', mode='w', encoding='utf8') as file:
        tagged = sorted(tagged.items(), key=lambda x: x[1], reverse=False)

        for key, value in tagged:
            file.write('{} | {}\n'.format(key, value))


if __name__ == "__main__":
    # ------------------------------------------------------------------------
    from fig2word import expandText

    text = open('transcript.txt', mode='r', encoding='utf8').read().split('\n')
    newtext = []
    for index, sent in enumerate(text):
        if index % 100 == 0:
            print(index, len(text))
        start, sent, line = sent.split('s>')
        if len(sent) > 0:
            expand = splitSentence(sent)
            # print("Input: ", sent)
            # print("Output:", expand)
            newtext.append('<s> {} </s> {}'.format(expand, line))
        else:
            print(index, "Sentence : ", sent)
    with open('new_transcript.txt', mode='w', encoding='utf8') as file:
        file.write('\n'.join(newtext))
    # ------------------------------------------------------------------------
    pass
