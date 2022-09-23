"""
Generates test set for various functions
"""
import nltk


def testset_typos(input_filename='./scraped/corpus.csv', output_filename='./test/typos.csv'):
    """
    Generates test set containing typos
    :param ouput_filename: saves it in the output_filename
    :return:
    """
    ENCODING = 'utf8'
    text = open(input_filename, encoding=ENCODING, mode='r').read()
    text = nltk.wordTokenizer(text) # cleans the text and tokenizes it into words
    typos = [word for word in text if nltk.isTypo(word)] # append to the list if the word is a typo
    typos = set(typos)

    with open(output_filename, mode='a', encoding=ENCODING) as file:
        for word in typos:
            file.write(word+'\n')

if __name__ == "__main__":
    testset_typos()