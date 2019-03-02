from dictionary_parser import get_dict
import os
import sense2vec

hdict = get_dict()
s2v = sense2vec.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reddit_vectors-1.1.0'))


#LexicalIndex parts of speech to Spacy parts of speech
pos_mapping = {
    'a': 'ADJ',
    'adv': 'ADV',
    'v': 'VERB',
    'conj': 'CONJ',
    'inj': 'INTJ',
    'n': 'NOUN',
    'prt': 'PART',
    'pron': 'PRON',
}


# Word vectors obviously have the problem of not dealing with multiple word senses, but wordnet similarity didn't work
# well at all so this is the best we've got
def find_by_vowelless_hebrew_and_english(hebrew_input, english_input):
    hebrew_candidates = hdict[hebrew_input]

    max_similarity = 0
    best_candidate = None
    winning_comparison = None

    for hebrew_word in hebrew_candidates:
        hebrew_word_pos = hebrew_word.pos.lower()
        hebrew_word_spacy_pos = pos_mapping[hebrew_word_pos]

        english_sense_lookup = english_input+'|'+hebrew_word_spacy_pos
        english_sense_vector = s2v[english_sense_lookup][1]

        hebrew_definition_sense_lookup = hebrew_word.meaning+'|'+hebrew_word_spacy_pos
        hebrew_definition_sense_vector = s2v[hebrew_definition_sense_lookup][1]

        similarity = s2v.data.similarity(english_sense_vector, hebrew_definition_sense_vector)

        if similarity > max_similarity:
            max_similarity = similarity
            best_candidate = hebrew_word
            winning_comparison = (english_sense_vector, hebrew_definition_sense_vector)


    return best_candidate








def test():
    res = find_by_vowelless_hebrew_and_english('טהור', 'pure')
    print(res)
    return res

if __name__ == '__main__':
    test()

