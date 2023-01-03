import re
import csv
import codecs
import argparse

"""
Process the sentence pairs in conversation extracted from cornell movie dialog corpus.

The processing includes formalizing string in the text using regular representation,
filtering according to text length, creating numerical representation for discreting
and triming infrequenctly seen words in the text.

This code refer the code on the pytorch tutorial given by
https://github.com/pytorch/tutorials/blob/main/beginner_source/chatbot_tutorial.py
"""

# Default word tokens
PAD = 0 # Used for padding short sentences
SOS = 1 # Start-of-sentence token
EOS = 2 # End-of-sentence token

MAX_LENGTH = 20 # Threshold for filtering sentence pairs
MIN_COUNT = 2 # The threshold for triming sentence pairs


def formalize(s):
    """
    Formalize the given string by removing all non-alphabet characters

    Args:
        s(<str>): the given string
    Return:
        (<str>): A processed string
    """
    # Turn a Unicode string to plain ASCII
    temp_str = (s.encode('ascii', 'ignore')).decode('utf-8')

    # Trim and remove all non-letter characters using regular expression
    temp_str = re.sub(r"([.!?])", r" \1", s)
    temp_str = re.sub(r"[^a-zA-Z.!?]+", r" ", s)  

    # Lowercase for final return
    return temp_str.lower().strip()


def filter(pairs, max_length=20):
    """
    Filter pairs that under max_length threshold

    Args:
        pairs (list<list<str>>): The given list of pairs
        max_length (int): The threshold for filtering pairs, default in 10
    Return:
        (list<list<str>>): The processed list of pairs that both length of sentences are under given max_length
    """
    return [p for p in pairs 
            if len(p[0].split(' ')) < max_length and len(p[1].split(' ')) < max_length]


class IndexMapping:
    """
    Map each unique word that encounter in the pairs to an index value
    Then represent and store the discrete space by a dictionary
    """
    def __init__(self) -> None:
        # self.name = name
        self.word2index = {} # encode the word into an integer
        self.index2word = {PAD: '<P>', SOS: '<S>', EOS: '<E>'} # decode the integer into a word
        self.word2count = {} # count the occurence time of words
        self.n_words = 3 # Count the SOS and EOS, then accumulate when new words come
        
    def add_word(self, word):
        # add the word into the dictionary and record its occurence time
        if word not in self.word2index:
            # If the word is new, then add it in the dictionary and count its number as 1
            self.word2index[word] = self.n_words
            self.index2word[self.n_words] = word 
            self.word2count[word] = 1            
            self.n_words += 1                    
        else:
            # If the word existed, just change its count number
            self.word2count[word] += 1

    def add_sentence(self, sentence):
        for word in sentence.split(' '):
            self.add_word(word)


def trim_mapping(mapping, min_count):
    """
    Trim the infrequently seen words in the given mapping 
    decided by the given minimum counts

    Args:
        mapping (dict): The given dict for triming
        min_count (int): The threshold for the minimum count for triming, 
                         the word count in the original dict below the min_count will be removed
    """
    keep_words = [] # Store all remaining words

    for k, v in mapping.word2count.items():
        if v > min_count:
            keep_words.append(k) # Remove all words that the count is less than the threshold 
    
    new_mapping = IndexMapping() # Create a new mapping
    
    for w in keep_words:
        new_mapping.add_word(w)
    
    return new_mapping


def trim_pairs(pairs, mapping):
    """ 
    Trim the infrequently seen words in the given list of pairs 
    decided by the given mapping
    
    Args:
        mapping (dict): the trim mapping that remove all infrequency seen words
        pairs (list<list<str>>): the pairs for triming based on the mapping
    Return:
        (list<list<str>>): the trimed pairs
    """
    keep_pairs = []

    for pair in pairs:
        keep_input, keep_output = True, True # Set flag for checking 

        # Check for the input sentence
        for word in pair[0].split(' '):
            if word not in mapping.word2index:
                keep_input = False
                break
        
        # Check for the output sentence
        for word in pair[1].split(' '):
            if word not in mapping.word2index:
                keep_output = False
                break
        
        # Only keep the pair if the input and output sentence pass both checking
        if keep_input and keep_output:
            keep_pairs.append(pair)
    
    #### An alternative for rewriting the code below ###
    # for pair in pairs:
    #     is_keep = True

    #     for index in range(2):
    #         for word in pair[index].split(' '):
    #             if word not in mapping.word2index:
    #                 is_keep = False
    #                 break

    #     if is_keep:
    #         keep_pairs.append(pairs)   
    
    return keep_pairs


def main():
    """
    Process and select sentence pairs for further processing
    """
    parser = argparse.ArgumentParser(description='Data processing for movie_corpus text')
    
    parser.add_argument('-i', '--input', required=True,help='Path to input dir')
    parser.add_argument('-o', '--output', required=True, help='Path to output file')

    args = parser.parse_args()

    # Convert args to dict
    vargs = vars(args)

    print("\nArguments:")
    for arg in vargs:
        print("{}={}".format(arg, getattr(args, arg)))
    
    print('\nLoading data...')
    with open('intermedium/loaded_movie_lines.txt') as f:
        read_in = f.read().strip().split('\n')
    
    print('\nFormalizing data...')
    formalized_pairs = [[formalize(s) for s in l.split('\t')] for l in read_in]
    filtered_pairs = filter(formalized_pairs, max_length=MAX_LENGTH)

    print('\nBuilding indexing mapping')
    num_map = IndexMapping()
    for p in filtered_pairs:
        num_map.add_sentence(p[0])
        num_map.add_sentence(p[1])
    
    print('\nTriming...')
    trim_num_map = trim_mapping(num_map, min_count=MIN_COUNT)
    selected_pairs = trim_pairs(filtered_pairs, trim_num_map)

    delimiter = str(codecs.decode('\t', "unicode_escape"))
    with open(args.output, 'w', encoding='utf-8') as outputfile:
        writer = csv.writer(outputfile, delimiter=delimiter, lineterminator='\n')

        for pair in selected_pairs:
            writer.writerow(pair)

    print("\nDone. Bye!")


if __name__ == '__main__':
    main()
