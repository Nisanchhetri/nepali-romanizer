import re
import os
import time
import doctest

num_to_word1 = {0: 'सुन्ना ', 1: 'एक ', 2: 'दुई ', 3: 'तिन ', 4: 'चार ', 5: 'पाँच ', 6: 'छ ', 7: 'सात ', 8: 'आठ ',
                9: 'नौ ',
                10: 'दस ', 11: 'एघार ', 12: 'बाह्र ', 13: 'तेह्र ', 14: 'चौध ', 15: 'पन्ध्र', 16: 'सोह्र ', 17: 'सत्र ',
                18: 'अठार ', 19: 'उन्नाइस ',
                20: 'बिस ', 21: 'एक्काइस ', 22: 'बाइस ', 23: 'तेइस ', 24: 'चौबिस ', 25: 'पच्चिस ', 26: 'छब्बिस ',
                27: 'सत्ताइस ', 28: 'अट्ठाइस ',
                29: 'उनन्तिस ', 30: 'तिस ', 31: 'एकतिस ', 32: 'बत्तिस ', 33: 'तेत्तिस ', 34: 'चौँतिस ', 35: 'पैँतिस ',
                36: 'छत्तिस ', 37: 'सैँतिस ',
                38: 'अठतिस ', 39: 'उनन्चालिस ', 40: 'चालिस ', 41: 'एकचालिस ', 42: 'बयालिस ', 43: 'त्रिचालिस ',
                44: 'चवालिस ', 45: 'पैँतालिस ',
                46: 'छयालिस ', 47: 'सतचालिस ', 48: 'अठचालिस ', 49: 'उनन्चास ', 50: 'पचास ', 51: 'एकाउन्न ',
                52: 'बाउन्न ', 53: 'त्रिपन्न ',
                54: 'चवन्न ', 55: 'पचपन्न ', 56: 'छपन्न ', 57: 'सन्ताउन्न ', 58: 'अन्ठाउन्न ', 59: 'उनन्साठी ',
                60: 'साठी ', 61: 'एकसट्ठी ', 62: 'बयसट्ठी ',
                63: 'त्रिसट्ठी ', 64: 'चौसट्ठी ', 65: 'पैँसट्ठी ', 66: 'छयसट्ठी ', 67: 'सतसट्ठी ', 68: 'अठसट्ठी ',
                69: 'उनन्सत्तरी', 70: 'सत्तरी ', 71: 'एकहत्तर ',
                72: 'बहत्तर ', 73: 'त्रिहत्तर ', 74: 'चौहत्तर ', 75: 'पचहत्तर ', 76: 'छयहत्तर ', 77: 'सतहत्तर ',
                78: 'अठहत्तर ', 79: 'उनासी ', 80: 'असी ',
                81: 'एकासी ', 82: 'बयासी ', 83: 'त्रियासी ', 84: 'चौरासी ', 85: 'पचासी ', 86: 'छयासी ', 87: 'सतासी ',
                88: 'अठासी ', 89: 'उनान्नब्बे ',
                90: 'नब्बे ', 91: 'एकानब्बे ', 92: 'बयानब्बे ', 93: 'त्रियानब्बे ', 94: 'चौरानब्बे ', 95: 'पन्चानब्बे ',
                96: 'छयानब्बे ', 97: 'सन्तानब्बे ',
                98: 'अन्ठानब्बे ', 99: 'उनान्सय '}

num_to_word2 = {100: 'सय ', 1000: 'हजार ', 100000: 'लाख ', 10000000: 'करोड ', 1000000000: 'अर्ब ',
                100000000000: 'खर्ब ', 10000000000000: 'नील ', 1000000000000000: 'पद्म ', 100000000000000000: 'शंख '}

nepali_to_english_digit = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8',
                           '९': '9'}


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print('Time required for %r :  %2.2f s' % \
                  (method.__name__, (te - ts)))
        return result

    return timed


def figure_to_word_nepali(*args):
    # Check if the iteration is first or not. If it is first iteration, only one arguement will be passed
    if len(args) == 1:
        number = args[0]
        word = ''
        first_entry = True

    else:
        number = args[0]
        word = args[1]
        first_entry = False

    length = len(number)

    # Checking the length of the number as the system can only convert 18 digit number
    if length < 19:
        # Converting the number which is in string format  into int
        number_int = int(number)
        length = len(str(number_int))

        if (length == 1) & (first_entry == True):
            return num_to_word1[number_int]
        elif (length == 2) & (first_entry == True):
            return num_to_word1[number_int]

        elif (length == 1) & (first_entry == False):
            if number_int != 0:
                word = word + num_to_word1[number_int]
            return word

        # Finding base of the number like for 2000 , 1000 is base
        if length < 5:
            n = 10 ** (length - 1)
        else:
            if length % 2 == 0:
                n = 10 ** (length - 1)
            else:
                n = 10 ** (length - 2)

        # Index for finding corresponding word for a digit
        index = int(number_int / n)

        if length > 2:
            if ((number[0] != '0')):
                word += num_to_word1[index] + num_to_word2[n]
        else:
            word += num_to_word1[number_int]

        end_number = number_int - ((number_int // n) * n)

        end_number_string = str(end_number)
        number_int_string = str(number_int)
        if len(end_number_string) == 1:
            if number_int_string[-2] != '0':
                return word

        return figure_to_word_nepali(str(end_number), word, first_entry)

    else:
        # print('Out of range')
        pass
        return number


def convert_nep_to_eng(number):
    """ Nepali digit to english digit to carryout further operations """
    numb_eng = ''
    for x in number:
        numb_eng += nepali_to_english_digit[x]
    return numb_eng


def updateText(text):
    """In this function we find numbers or alphanumeric value from our text corpus"""

    # text = "१आ ००००० १०.०० काका १लाला ७६७६७; १०ः०९ ९८९क  दादा मामा १२११ ८९०७८९ ९८७६५५ क१क १क१"
    # text = "००७२ ७२००"
    updated_text = ''
    # text = '१०-२०  २०-१० जजसकसक काका'
    for index, sentence in enumerate(text.splitlines()):
        # if index % 10 == 0:
        #     print('Index : ', index)

        updatedSentence = []
        for index, word in enumerate(sentence.split(' ')):
            # if index % 100000 == 0:
            #     print('Index : ', index//100000)

            # Find nepali digits in text
            # 1.01, +1000, -1000, 10:10, 11karod, 10-10
            number = re.findall(r"[-+]?\d*\.\d+|\d*\:\d+|\d*\-\d+|\d*\–\d+|\d+", word)
            # number = re.findall(r'\d*\w\w+',word)
            if number:
                figure = ''.join(number)
                
                #print("Figure:", figure)

                # Check if the word is alpha numeric or not
                nonNumeric = re.sub(r"\d|\.|\:|\-|\–", " ", word)
                nonNumeric = nonNumeric.split()

                # find number with decimal value
                if '.' in figure:

                    for i, decimal in enumerate(figure.split('.')):
                        # Use for converting to decimal
                        if i == 0:
                            figure = decimal
                            try:
                                word_nepali = figure_to_word_nepali(figure)
                                word = word_nepali
                            except:
                                word = figure
                                # print("Cant convert {} into word".format(figure))

                        # To write number after decimal like 1.23 as Ek dasamalab dui tin  instead of Ek dasamalab teis
                        else:
                            decimal_digit = ''
                            if len(decimal) != 0:
                                for x in decimal:
                                    decimal_digit += num_to_word1[int(x)]
                                word += 'दसमलब ' + decimal_digit
                                # print(word)
                elif ('–' in figure) or ('-' in figure):
                    word_nepali = ''
                    if '–' in figure:
                        for number_from_time in figure.split('–'):
                            try:
                                word_nepali += figure_to_word_nepali(number_from_time)
                            except:
                                # print("Cant convert {} into word".format(figure))
                                pass

                    else:
                        for number_from_time in figure.split('-'):
                            try:
                                word_nepali += figure_to_word_nepali(number_from_time)
                            except:
                                # print("Cant convert {} into word".format(figure))
                                pass
                    word = word_nepali


                # Find numbers representing time
                elif re.findall(r"\:", figure):
                    word_nepali = ''
                    for number_from_time in figure.split(':'):
                        try:
                            # To avoid 10:00 being written Dus sunna
                            if figure_to_word_nepali(number_from_time) != 'सुन्ना ':
                                word_nepali += figure_to_word_nepali(number_from_time)
                        except:
                            # print("Cant convert {} into word".format(figure))
                            pass
                    word = word_nepali
                    # print(word)


                else:
                    word = figure_to_word_nepali(figure)

                if (len(nonNumeric) != 0) & (''.join(nonNumeric) not in ('–', '-')):
                    word += ''.join(nonNumeric)
                else:
                    word = word

            else:
                word = word

            updatedSentence.append(word)
        # print(updatedSentence)
        updated_text += ' '.join(updatedSentence)

    return updated_text

def test():
    """
    #Test for updateText
    >>> updateText('१००१')
    'एक हजार एक '
    >>> updateText('११११११')
    'एक लाख एघार हजार एक सय एघार '
    >>> updateText('५०.५०')
    'पचास दसमलब पाँच सुन्ना '
    >>> updateText('०१००')
    'एक सय '
    >>> updateText('१०:१०')
    'दस दस '
    >>> updateText('म १०ओटा अण्डा खान्छु ')
    'म दस ओटा अण्डा खान्छु '
    >>> updateText('')
    ''
    """
    print(doctest.testmod())


def updateText_test(word=''):
    """In this function we find numbers or alphanumeric value from our text corpus"""

    # text = "१आ ००००० १०.०० काका १लाला ७६७६७; १०ः०९ ९८९क  दादा मामा १२११ ८९०७८९ ९८७६५५ क१क १क१"
    # text = "००७२ ७२००"

    updated_text = ''

    # Find nepali digits in text
    number = re.findall(r"[-+]?\d*\.\d+|\d*\ः\d+|\d*\-\d+|\d*\–\d+|\d+", word)
    
    # If the given word was number
    if number:
        # print(number)
        figure = ''.join(number)

        # Check if the word is alpha numeric or not
        nonNumeric = re.sub(r"\d|\.|\ः|\-|\–", " ", word)
        nonNumeric = nonNumeric.split()

        # find number with decimal value
        if '.' in figure:

            firstpart, secondpart = figure.split('.')

            figure = firstpart
            try:
                word = figure_to_word_nepali(figure)
            except:
                word = figure
                # print("Cant convert {} into word".format(figure))

                # To write number after decimal like 1.23 as Ek dasamalab dui tin  instead of Ek dasamalab teis
            decimal_digit = ''
            if len(secondpart) != 0:
                for digit in secondpart:
                    decimal_digit += num_to_word1[int(digit)]

                word += 'दसमलब ' + decimal_digit

        elif ('–' in figure) or ('-' in figure):
            word_nepali = ''
            if '–' in figure:
                for number_from_time in figure.split('–'):
                    try:
                        word_nepali += figure_to_word_nepali(number_from_time)
                    except:
                        # print("Cant convert {} into word".format(figure))
                        pass

            else:
                for number_from_time in figure.split('-'):
                    try:
                        word_nepali += figure_to_word_nepali(number_from_time)
                    except:
                        # print("Cant convert {} into word".format(figure))
                        pass
            word = word_nepali


        # Find numbers representing time
        elif re.search(r"\ः", figure):
            print(figure)
            word_nepali = ''
            for number_from_time in figure.split('ः'):
                try:
                    # To avoid 10:00 being written Dus sunna
                    if figure_to_word_nepali(number_from_time) != 'सुन्ना ':
                        word_nepali += figure_to_word_nepali(number_from_time)
                except:
                    # print("Cant convert {} into word".format(figure))
                    pass
            word = word_nepali
            # print(word)

        else:
            word = figure_to_word_nepali(figure)

        if (len(nonNumeric) != 0) & (''.join(nonNumeric) not in ('–', '-')):
            word += ''.join(nonNumeric)
        else:
            word = word

    else:
        word = word

    return word


def nepali_shortform_splitter(text):
    """Split nepali short form
        Example: मा.प.से = मा प से """
    final_text = ''

    for i, sentence in enumerate(text.splitlines()):
        # print(i)
        updatedSentence = []
        for word in sentence.split(' '):
            if '.' in word:
                combined_word = ''
                for splited_word in word.split('.'):
                    combined_word += splited_word + ' '
                word = combined_word

            updatedSentence.append(word)
            # print(updatedSentence)

        final_text += ' '.join(updatedSentence)

    return final_text


# @timeit
def expandText(text=''):
    """
    Expand text : 1-> one
    I.O.E -> I O E
    :param text:
    :return:
    """

    # Convert Nepali digits to word
    text = updateText(text)

    # Split short form
    text = nepali_shortform_splitter(text)

    return text


def expandTextDir(input_dir='./original', output_dir='./updated'):
    """
    Expand text from a directory and save it in output directory
    """

    # If the input_dir doesn't exist break
    if not os.path.exists(input_dir):
        print('Input Directory Does Not Exist. Breaking . . .')
    assert os.path.exists(input_dir)

    # If the output directory doesn't exist, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # read all the scripts in the input_dir
    # we do not want to read images in the directory and get error
    import glob
    filenames_txt = glob.glob(os.path.join(input_dir, '*.txt'))
    filenames_csv = glob.glob(os.path.join(input_dir, '*.csv'))
    filenames = filenames_csv + filenames_txt
    print("Files in directory: {}".format(filenames))

    for filename in filenames:
        try:
            text = open(filename, mode='r', encoding='utf8').read()
            expanded_text = expandText(text)

            # save updated text in a file
            with open(os.path.join(output_dir, os.path.basename(filename)), mode="w", encoding="utf-8") as file:
                file.write(expanded_text)
                # print("File updated and saved !")

        except:
            print('Can not update {}'.format(filename))


if __name__ == '__main__':
    # expandTextDir()
    # To test if text generated by
##    text1 = open('./scraped/sentence_corpus_1.txt', mode='r', encoding='utf8').read()
##    text2 = open('./scraped/sentence_corpus.txt', mode='r', encoding='utf8').read()
##    assert text1 == text2
    test()
