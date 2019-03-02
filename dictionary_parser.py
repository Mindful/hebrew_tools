import xml.etree.ElementTree
import logging
import unicodedata
from collections import defaultdict

SCHEMA_PREFIX = '{http://openscriptures.github.com/morphhb/namespace}'
ENTRY_TYPE = SCHEMA_PREFIX + 'entry'

ENTRY_POS = SCHEMA_PREFIX + 'pos'
ENTRY_DEFINITION = SCHEMA_PREFIX + 'def'
ENTRY_WORD = SCHEMA_PREFIX + 'w'

WORD_PRONUNCIATION = 'xlit'
ENTRY_ID = 'id'

LOGGER_NAME = 'hdict'


def strip_nikud_vowels(string):
    normalized = unicodedata.normalize('NFKD', string)
    return ''.join([c for c in normalized if not unicodedata.combining(c)])


class DictionaryParseException(Exception):
    pass


class DictionaryEntry(object):
    __slots__ = ('dict_id', 'word', 'word_vowelless', 'pronunciation', 'meaning', 'pos')

    def __init__(self, dict_id, word, meaning, pos):
        for attr in self.__slots__:
            setattr(self, attr, None)
        self.dict_id = dict_id
        if word is not None:
            self.word = word.text
            self.word_vowelless = strip_nikud_vowels(self.word)
            self.pronunciation = word.attrib[WORD_PRONUNCIATION]
        if meaning is not None:
            self.meaning = meaning.text.lower()
        if pos is not None:
            self.pos = pos.text

    def dict_key(self):
        return self.word_vowelless

    def missing_attributes(self):
        return [attr for attr in self.__slots__ if getattr(self, attr) is None]

    def is_complete_entry(self):
        return len(self.missing_attributes()) == 0


class DictionaryParser(object):
    def __init__(self, file_name):
        self.file_name = file_name
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(LOGGER_NAME)
        self.dictionary = self.construct_dictionary()

    def construct_dictionary(self):
        tree = xml.etree.ElementTree.parse(self.file_name)
        root = next(part for part in tree.getroot().iter('{http://openscriptures.github.com/morphhb/namespace}part') if
                    part.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'heb')
        dictionary = defaultdict(list)
        entry_counter = 0
        for entry in root.iter('{http://openscriptures.github.com/morphhb/namespace}entry'):
            entry_object = self.processEntry(entry)
            entry_counter += 1
            if entry_object:
                key = entry_object.dict_key()
                if key:
                    dictionary[key].append(entry_object)
                else:
                    self.logger.error("Could not generate key for entry with id "+entry_object.dict_id)

        self.logger.info("Scanned " + str(entry_counter) + " raw entries")
        self.logger.info("Generated " + str(len(dictionary)) + " dictionary entries")
        return dictionary

    def processEntry(self, entry):
        dict_id = entry.attrib[ENTRY_ID]

        word = entry.find(ENTRY_WORD)
        pos = entry.find(ENTRY_POS)
        definition = entry.find(ENTRY_DEFINITION)

        for sub_element in [(word, 'word'), (pos, 'part of speech'), (definition, 'definition')]:
            if sub_element[0] is None:
                self.logger.warning('Could not find ' + sub_element[1] + ' for dictionary entry with id ' + dict_id)

        result = DictionaryEntry(dict_id, word, definition, pos)
        return result


def get_dict():
    parser = DictionaryParser('LexicalIndex.xml')
    return parser.dictionary


if __name__ == '__main__':
    get_dict()
