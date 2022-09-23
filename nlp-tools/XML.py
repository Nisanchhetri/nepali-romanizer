from xml.etree import ElementTree
from collections import deque
import os
import re
import json


class TrainFile:
    '''
    Represents the pos-tagged xml file
    '''
    tags = {}

    def __init__(self, filename):
        """

        :param filename: Relative or absolute path of the file to be parsed
        :type filename: str
        """
        self.filename = filename
        self.elementTree = ElementTree.parse(filename)
        self.body = self.elementTree.getroot().find('text').find('body')
        self.tags = set()

    def __iter__(self):
        """

        :return: Iterator that returns a sentence in each iteration.
        Sentence is in the form [ ("Word1", "Tag1"), ("Word2", "Tag2), ("Word3","Tag3) ]
        i.e : list of tuples
        :rtype: iter of list
        """
        # queue maintains all the xml elements. elements might have tags inside it.
        # put all the body element into the queue
        queue = deque(self.body)
        while len(queue) > 0:
            # pop a element from the queue
            node = queue.pop()

            # if extracted element is a sentence
            if node.tag == 's':
                # results will contain the list of tokens in the sentence.
                result = []
                # iterate over each token in the sentence
                for x in node:
                    # if the the tag name of tokein starts with I eg: IKM,IA,II,IE, IH etc.
                    # then it must be joined with previous word
                    # but if it's in the begining of sentence, it need not be done so.
                    if x.attrib['ctag'].startswith("I") and len(result) > 0:
                        t = result[-1]
                        result[-1] = (t[0] + x.text, t[1])
                    elif x.attrib['ctag'] in ("MLF", "MLO") and len(result) > 0:
                        t = result[-1]
                        result[-1] = (t[0] + x.text, t[1])
                    else:
                        # split the text in the range of nepali character
                        # if it can be splitted, then there is a weird character in the word
                        # otherwise the word is fine.
                        s = re.split('[\u0900-\u097F]+', x.text)
                        if len(s) < 3:
                            if len(s) == 2:
                                # if all the characters are nepali unicode characters
                                if s[0] == '' and s[1] == '':
                                    self.tags.add(x.attrib['ctag'])
                                    result.append((x.text, x.attrib['ctag']))
                                else:
                                    # this should not happen, it's a weird word.
                                    # print("Weird word found :", s)
                                    pass
                            else:
                                self.tags.add(x.attrib['ctag'])
                                result.append((x.text, x.attrib['ctag']))
                        else:
                            # this should not happen
                            # print("Weird word found :", s)
                            pass
                yield result
            else:
                for x in node:
                    queue.appendleft(x)
        raise StopIteration

    def sentence_tagger_iter(self):
        """
        :return: Iterator that returns a sentence per iteration.
        Sentence is in the form ( "Word1 Word2 Word3", {'tags': ["Tag1","Tag2","Tag3"]} )
        i.e :  tuple with first element the sentence and second element as list of tags for the sentence
        :rtype: iter of tuple
        """
        for x in self:
            yield (' '.join(a[0] for a in x), {'tags': [a[1] for a in x]})
        raise StopIteration

    def sentences_iter(self):
        """
        :return: Iter that returns a user readable sentence in xml file per iteration.
        :rtype: iter of str
        """
        for x in self:
            one = ' '.join(a[0] for a in x)
            two = one.replace(' ,', ',')
            three = two.replace(' ।', '।')
            four = three.replace(' ?', '?')
            five = four.replace(' – ', '–')
            yield (five.replace(' !', '!'))
        raise StopIteration

    @staticmethod
    def test_sentences_n_tagger():
        """
        Performs test of sentence generation of the sentences in text
        :return:None
        :rtype: None
        """
        file = TrainFile('test_file.xml')
        expected = json.load(open('test_expectation.json'))
        for got, required in zip(file.sentence_tagger_iter(), expected):
            assert got[0] == required[0] and got[1] == required[1]


def parserAllXMLFiles(input_dir='./XML/', output_dir='./parsedXML2/'):
    import glob

    files = glob.glob(os.path.join(input_dir, '*.xml'))

    # If output_dir doesn't exist, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for index, filename in enumerate(files):
        try:
            print('Processing {} / {} : {}'.format(index, len(files), filename))

            # Get all the sentences in the XML File
            # parser = TrainFile("test_file.xml")
            parser = TrainFile(filename)
            all_sentence = parser.sentences_iter()

            # Save the sentences to a text file
            output_filename = os.path.join(output_dir, filename.split('\\')[1])
            with open(output_filename, mode='w', encoding='utf8') as output_file:
                for sentence in all_sentence:
                    output_file.write(sentence + '\n')
        except:
            print('Couldn"t parse : {}', filename)


# test TrailFile sentence generation
if __name__ == "__main__":
    parserAllXMLFiles()
    # TrainFile.test_sentences_n_tagger()
