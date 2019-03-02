import csv
from lookup import Lookup

def process_csv(filename):

    with open(filename, 'r') as input_file:
        input = csv.reader(input_file)
        results = []

        lookup = Lookup()

        for row in input:
            results.append(lookup.find_by_vowelless_hebrew_and_english(row[0].strip(), row[1].strip()))

        output = [(word.word_vowelless, word.word, word.meaning) for word in results if word is not None]

        with open('card_output.csv', 'w') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(output)

def test():
    process_csv('input.csv')

if __name__ == '__main__':
    test()