import os
import string
import re

import hunspell

from rom_to_ne_own_dic import dic


class NepaliConversion:
    
    def __init__(self):
        '''This class takes roman english sentence as input and splits into words and 
        checks individual word in english and nepali dictionary and return all possible
        combinations of sentences.
        '''
        self.MODULE_PATH = os.path.split(__file__)[0]        
        self.checker_ne = hunspell.HunSpell(
            os.path.join(self.MODULE_PATH, 'nlp-tools/dict/ne_NP.dic'),
            os.path.join(self.MODULE_PATH, 'nlp-tools/dict/ne_NP.aff')
        )
        self.checker_en = hunspell.HunSpell(
            os.path.join(self.MODULE_PATH, 'nlp-tools/dict/en_US.dic'),
            os.path.join(self.MODULE_PATH, 'nlp-tools/dict/en_US.aff')
        )

        with open(os.path.join(self.MODULE_PATH, 'word_list.txt')) as file1, \
             open(os.path.join(self.MODULE_PATH, 'word_list_2.txt')) as file2, \
             open(os.path.join(self.MODULE_PATH, 'word_list_rem.txt')) as file3:

            self.com_both = set(file1.read().split())
            self.com_2 = set(file2.read().split())
            self.com_rem = set(file3.read().split())
           
    def convert_sentence(self, sentence):
        sentence = sentence.lower()
        word_store = self.check_valid_sentence(sentence)
        word_store = self.remove_empty_list(word_store)
        final_sen = self.final_sentence(word_store) 

        return final_sen   
    
    def convert_word(self, word): 
        '''return all possible nepali word of roman english from
        own roman to nepali dictinary'''
        word_len = len(word)
        sen = []
        count = 0
        for i in range(word_len):
            for j in range(word_len, 0, -1):
                chunk = word[count:j]
                if dic.get(chunk):
                    count += len(chunk)
                    sen.append(dic[chunk])
                    break

        return_word = []
        if sen:
            return_word = sen[0]
            len_sen = len(sen)
            for i in range(1, len_sen):
                temp_list = []
                for char in sen[i]:
                    temp_list.extend([c + char for c in return_word])
                return_word = temp_list
          
        return return_word
    
    def check_valid_sentence(self, sentence):
        ''' return all possible words present in english, nepali and both
        dictionary. if not available in both dic, return as it is.'''
        word_store = []
        sentence = sentence.strip().split(" ")
        
        for i, char in enumerate(sentence):
            word_store.append([])
            if char in self.com_both:
                if char in self.com_2:
                    word_store[i].append(char)
                elif char in self.com_rem:
                    word_store[i].append(char)
                    word_list = self.convert_word(char)
                    if word_list:
                        for word in word_list:
                            if self.checker_ne.spell(word):
                                checker = self.checker_ne.spell(word)
                                word_store[i].append(word)
                else:
                    word_list = self.convert_word(char)
                    if word_list:
                        for word in word_list:
                            if self.checker_ne.spell(word):
                                checker = self.checker_ne.spell(word)
                                word_store[i].append(word)
            else:
                if self.checker_en.spell(char):
                    checker = self.checker_en.spell(char)
                    word_store[i].append(char)
                else:
                    test_count = 0
                    word_list = self.convert_word(char)
                    if word_list:
                        for word in word_list:
                            if self.checker_ne.spell(word):
                                checker = self.checker_ne.spell(word)
                                word_store[i].append(word)
                                test_count = 1
                    if test_count == 0:
                        word_store[i].append(char)          

        return word_store
    
    def remove_empty_list(self, word_store):  
        '''to remove all blank list present in the possible sentences'''
        for char in word_store:
            if [] in word_store:
                word_store.remove([])

        return word_store
    
    def final_sentence(self, word_store): 
        '''combine all possible words present in word_store to form one 
        sentence'''
        if len(word_store):
            word_0 = word_store[0]
            l_all = len(word_store)
            for i in range(1, l_all):
                temp_list = []
                for char_app in word_store[i]:
                    new_list = [char + ' ' + char_app for char in word_0]
                    temp_list.extend(new_list)
                word_0 = temp_list
        return word_0

while True:
    convert = NepaliConversion()
    sen = input("Enter sentence to romanize:")
    print("sentence length:", len(convert.convert_sentence(sen)),"\n")
    output = str(convert.convert_sentence(sen))
    with open("romanized.txt", "w+") as f:
        f.write(output)
