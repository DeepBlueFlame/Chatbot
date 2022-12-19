import os
import csv
import codecs
import argparse

"""
Load the cornell movie dialog corpus.
Available from here:
http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html

The code is directly used the github code in the following link:
https://github.com/floydhub/textutil-preprocess-cornell-movie-corpus.git
This code has a slight modification compared to the original code  
"""


# Define a fields in a line for fields extraction
MOVIE_LINES_FIELDS = ["LINE_ID", "CHARACTER_ID", "MOVIE_ID", "CHARACTER", "TEXT"]
# Define conversation properties
MOVIE_CONVERSATIONS_FIELDS = ["CHARACTER1_ID", "CHARACTER2_ID", "MOVIE_ID", "UTTERANCE_IDS"]


def load_lines(file_name, fields):
    """
    A function to create a dictionary in the above shown format covering all lines in the corpus

    Args:
        file_name(str): file to read
        fields(list<str>): fileds to extract
    Return:
        dict<dict<str>>: the extracted fileds for each line
    """
    lines = {}

    # Check the LINE_ID is included in the fields set
    assert 'LINE_ID' in fields, "The given fields set does not contain 'LINE_ID'"

    with open(file_name, 'r', encoding='iso-8859-1') as f:
        for line in f:
            # Convert the line into a values list according to the spliting result 
            values = line.split(" +++$+++ ")

            line_obj = {}
            for i, field in enumerate(fields):
                line_obj[field] = values[i]
            
            lines[line_obj['LINE_ID']] = line_obj
    
    return lines


def match_conversation(file_name, lines, fileds):
    """
    According to loaded lines, match lines as a conversation

    Args:
        file_name (str): file to load
        lines (dict<dict<str>>): lines dictionary read previously
        fields(list<str>): the defined fields for each line
    Return:
        list<dict>: a list of dictionary contains charaters, movie id, utterance ids and conversational lines
    """
    conversations = []

    with open(file_name, 'r', encoding='iso-8859-1') as f:
        for line in f:
            values = line.split(" +++$+++ ")

            conv_obj = {}
            for i, field in enumerate(fileds):
                conv_obj[field] = values[i]
            
            # Convert string to list (conv_obj["UTTERANCE_IDS"] == "['L598485', 'L598486', ...]")
            line_ids = eval(conv_obj['UTTERANCE_IDS'])

            conv_obj['LINES'] = []
            for line_id in line_ids:
                conv_obj['LINES'].append(lines[line_id])
            
            conversations.append(conv_obj)
    
    return conversations


def extract_conversation_sentence_pairs(converations):
    """
    Extract sentences pair from the conversation dictionary

    Arg:
        conversations(list<dict>)
    Return:
        list<list<str>>: a list of conversational sentence pairs
    """
    pairs = []

    for conv in converations:
        
        # for i in range(len(conv['LINES']) - 1):
        #     initial_line = conv['LINES'][i]['TEXT'].strip()
        #     response_line = conv['LINES'][i+1]['TEXT'].strip()
        
        #     if initial_line and response_line:
        #         pairs.append([initial_line, response_line])
        
        # Use every two sentences in the LINES to form a converstional pair
        counter = 0
        while counter < len(conv['LINES']) - 1:
            initial_line = conv['LINES'][counter]['TEXT'].strip()
            response_line = conv['LINES'][counter+1]['TEXT'].strip()

            if initial_line and response_line:
                pairs.append([initial_line, response_line])
            
            counter += 1
    
    return pairs


def main():
    """
    Parses the Cornell Movie Dialog Corpus, and extracts conversations from it.
    """

    # Parse command line args
    parser = argparse.ArgumentParser(description='Extract conversations from Cornell movie dialog corpus')

    parser.add_argument('-i', '--input', required=True,
                        help='Path to input dir')
    parser.add_argument('-d', '--delimiter', required=True, default='\t', 
                        help='Column delimiter between output columns')
    parser.add_argument('-o', '--output', required=True, help='Path to output file')

    args = parser.parse_args()
    # Unescape the delimiter
    args.delimiter = codecs.decode(args.delimiter, "unicode_escape")

    # Convert args to dict
    vargs = vars(args)

    print("\nArguments:")
    for arg in vargs:
        print("{}={}".format(arg, getattr(args, arg)))

    lines = {}
    conversations = []

    print("\nProcessing corpus...")
    lines = load_lines(os.path.join(args.input, "movie_lines.txt"), MOVIE_LINES_FIELDS)

    print("\nLoading conversations...")
    conversations = match_conversation(os.path.join(args.input, "movie_conversations.txt"),
                                      lines, MOVIE_CONVERSATIONS_FIELDS)

    delimiter = str(codecs.decode('\t', "unicode_escape"))
    with open(args.output, 'w', encoding='utf-8') as outputfile:
        writer = csv.writer(outputfile, delimiter=delimiter, lineterminator='\n')
        
        for pair in extract_conversation_sentence_pairs(conversations):
            writer.writerow(pair)

    print("\nDone. Bye!")

if __name__ == '__main__':
    main()
