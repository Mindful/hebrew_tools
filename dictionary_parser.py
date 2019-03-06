import xml.etree.ElementTree
import logging
import unicodedata
from collections import defaultdict

LEXICAL_INDEX = 'LexicalIndex.xml'
BROWN_DRIVER_BRIGGS = 'BrownDriverBriggs.xml'

SCHEMA_PREFIX = '{http://openscriptures.github.com/morphhb/namespace}'
ENTRY_TYPE = SCHEMA_PREFIX + 'entry'
PART_TYPE = SCHEMA_PREFIX + 'part'

PART_LANGUAGE = '{http://www.w3.org/XML/1998/namespace}lang'

ENTRY_POS = SCHEMA_PREFIX + 'pos'
ENTRY_DEFINITION = SCHEMA_PREFIX + 'def'
ENTRY_WORD = SCHEMA_PREFIX + 'w'
ENTRY_XREF = SCHEMA_PREFIX + 'xref'

WORD_PRONUNCIATION = 'xlit'
ENTRY_ID = 'id'

LOGGER_NAME = 'hdict'

#TODO: We could get gender information for some nouns from BrownDriverBriggss


def strip_nikud_vowels(string):
    normalized = unicodedata.normalize('NFKD', string)
    return ''.join([c for c in normalized if not unicodedata.combining(c)])


class DictionaryParseException(Exception):
    pass


class DictionaryEntry(object):
    __slots__ = ('dict_id', 'word', 'word_vowelless', 'pronunciation', 'meaning', 'pos', 'gender')

    def __init__(self, dict_id, word, meaning, pos, gender):
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
        #TODO: gender

    def dict_key(self):
        return self.word_vowelless

    def missing_attributes(self):
        return [attr for attr in self.__slots__ if getattr(self, attr) is None]

    def is_complete_entry(self):
        return len(self.missing_attributes()) == 0


class DictionaryParser(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger(LOGGER_NAME)
        self.dictionary = self.construct_dictionary()

    def process_bdb(self):
        tree = xml.etree.ElementTree.parse(BROWN_DRIVER_BRIGGS)
        hebrew_parts = (part for part in tree.getroot().iter(PART_TYPE) if part.attrib[PART_LANGUAGE] == 'heb')
        dictionary = {}
        for part in hebrew_parts:
            for entry in part.iter(ENTRY_TYPE):
                entry_id = entry.attrib[ENTRY_ID]
                if entry_id in dictionary:
                    self.logger.warning("Duplicate BDB entry with id "+id)
                dictionary[entry.attrib[ENTRY_ID]] = entry

        return dictionary


    def construct_dictionary(self):
        self.brown_driver_briggs = self.process_bdb()

        tree = xml.etree.ElementTree.parse(LEXICAL_INDEX)
        hebrew_root = next(part for part in tree.getroot().iter(PART_TYPE) if part.attrib[PART_LANGUAGE] == 'heb')
        dictionary = defaultdict(list)
        entry_counter = 0
        for entry in hebrew_root.iter(ENTRY_TYPE):
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
        xref = entry.find(ENTRY_XREF)

        for sub_element in [(word, 'word'), (pos, 'part of speech'), (definition, 'definition'),
                            (xref, 'external references')]:
            if sub_element[0] is None:
                self.logger.warning('Could not find ' + sub_element[1] + ' for dictionary entry with id ' + dict_id)

        if xref is not None and xref.attrib.get('bdb') is not None:
            bdb_entry = self.brown_driver_briggs[xref.attrib['bdb']]
            bdb_pos = bdb_entry.find(ENTRY_POS)
            if bdb_pos is not None:
                print("derpy")


        result = DictionaryEntry(dict_id, word, definition, pos, xref.attrib)
        return result


def get_dict():
    parser = DictionaryParser()
    return parser.dictionary


if __name__ == '__main__':
    get_dict()
