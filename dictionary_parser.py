import xml.etree.ElementTree
import logging
import unicodedata


SCHEMA_PREFIX = '{http://openscriptures.github.com/morphhb/namespace}'
ENTRY_TYPE = SCHEMA_PREFIX +'entry'

ENTRY_POS = SCHEMA_PREFIX +'pos'
ENTRY_DEFINITION = SCHEMA_PREFIX + 'def'
ENTRY_WORD = SCHEMA_PREFIX + 'w'

WORD_PRONUNCIATION = 'xlit'
ENTRY_ID = 'id'

LOGGER_NAME = 'hdict'


def strip_nikud_vowels(string):
	normalized=unicodedata.normalize('NFKD', string)
	return ''.join([c for c in normalized if not unicodedata.combining(c)])

class DictionaryParseException(Exception):
	pass

class DictionaryEntry(object):
	__slots__ = ('dict_id', 'word', 'word_vowelless', 'pronunciation', 'meaning', 'pos')

	def __init__(self, dict_id, word, pronunciation, meaning, pos):
		self.dict_id = dict_id
		self.word = word
		self.word_vowelless = strip_nikud_vowels(word)
		self.pronunciation = pronunciation
		self.meaning = meaning
		self.pos = pos

	def dict_key(self):
		return (self.word_vowelless, self.meaning)


class DictionaryParser(object):
	def __init__(self, file_name):
		self.file_name = file_name
		self.logger = logging.getLogger(LOGGER_NAME)
		self.dictionary = self.construct_dictionary()


	def construct_dictionary(self):
		tree = xml.etree.ElementTree.parse(self.file_name)
		root = tree.getroot()
		dictionary = {}
		for entry in root.iter('{http://openscriptures.github.com/morphhb/namespace}entry'):
			entry_object = self.processEntry(entry)
			if entry_object:
				key = entry_object.dict_key()
				if key in dictionary:
					raise DictionaryParseException(str(key) + ' encountered twice')
				else:
					dictionary[key] = entry_object

		return dictionary



	def processEntry(self, entry):
		dict_id = entry.attrib[ENTRY_ID]

		word = entry.find(ENTRY_WORD)
		pos = entry.find(ENTRY_POS)
		definition = entry.find(ENTRY_DEFINITION)

		for sub_element in [(word, 'word'), (pos, 'part of speech'), (definition, 'definition')]:
			if sub_element[0] is None:
				self.logger.warn('Could not find '+sub_element[1]+' for dictionary entry with id '+dict_id)
				return None


		result = DictionaryEntry(dict_id, word.text, word.attrib[WORD_PRONUNCIATION], pos.text, definition.text)
		return result


def get_dict():
	parser = DictionaryParser('LexicalIndex.xml')
	return parser.dictionary

