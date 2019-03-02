from dictionary_parser import get_dict
import os
import sense2vec
import logging


class Lookup(object):
    def __init__(self):
        self.hdict = get_dict()
        self.s2v = sense2vec.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reddit_vectors-1.1.0'))

        #LexicalIndex parts of speech to Spacy parts of speech
        self.pos_mapping = {
            'a': 'ADJ',
            'adv': 'ADV',
            'v': 'VERB',
            'conj': 'CONJ',
            'inj': 'INTJ',
            'n': 'NOUN',
            'prt': 'PART',
            'pron': 'PRON',
        }

        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger('lookup')


    # Word vectors obviously have the problem of not dealing with multiple word senses,
    # but wordnet similarity didn't work well at all so this is the best we've got
    def find_by_vowelless_hebrew_and_english(self, hebrew_input, english_input):
        hebrew_candidates = self.hdict[hebrew_input]

        max_similarity = 0
        best_candidate = None
        winning_comparison = None

        for hebrew_word in hebrew_candidates:
            hebrew_word_pos = hebrew_word.pos

            if hebrew_word_pos is not None and hebrew_word_pos.lower() in self.pos_mapping:
                hebrew_word_spacy_pos = self.pos_mapping[hebrew_word_pos.lower()]

                english_sense_lookup = english_input+'|'+hebrew_word_spacy_pos
                english_sense_vector = self.s2v[english_sense_lookup][1]

                hebrew_definition_sense_lookup = hebrew_word.meaning+'|'+hebrew_word_spacy_pos
                hebrew_definition_sense_vector = self.s2v[hebrew_definition_sense_lookup][1]

                similarity = self.s2v.data.similarity(english_sense_vector, hebrew_definition_sense_vector)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_candidate = hebrew_word
                    winning_comparison = (english_sense_vector, hebrew_definition_sense_vector)
            else:
                self.logger.warning("Unrecognized or missing pos "+str(hebrew_word_pos)+" for hebrew word "+hebrew_word.word+", skipping")


        return best_candidate








def test():
    lookup = Lookup()
    res = lookup.find_by_vowelless_hebrew_and_english('טהור', 'pure')
    print(res)
    return res

if __name__ == '__main__':
    test()

