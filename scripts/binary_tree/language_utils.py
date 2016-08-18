import sys
import pprint
from pycorenlp import StanfordCoreNLP
import json
import re
from enum import IntEnum
import parsedatetime as pdt
from datetime import datetime

sys.path.insert(0, '/Volumes/anupam_work/code/nlp-code/scripts/binary_tree/')
import language_functions_binary as lang

possibleNegTags = ['neg']
possible_negative_words = ['no', 'not']
nlp = StanfordCoreNLP('http://localhost:9000')

final_state = -1

def parse_number(user_input):
    val = re.findall(r'\d+\.?\d+', user_input)
    if len(val) > 0:
        return val[0]
    else:
        return -1
    
def parse_date_time(user_input):
    cal = pdt.Calendar()
    val_set = cal.parseDT(user_input)
    if len(val_set) > 0:
        return True, val_set[0]
    else:
        return False, None
    
def safe_get(dic, enum_key, default = 0):
    if enum_key in dic:
        return dic[enum_key]
    return default

def is_equal_arr(arr_1, arr_2):
        len_1 = len(arr_1)
        len_2 = len(arr_2)
        if len_1 != len_2:
            return False
        for idx, val in enumerate(arr_1):
            val_n = val.lower().strip()
            val_2 = arr_2[idx]
            val_2_n = val_2.lower().strip()
            if val_n != val_2_n:
                return False
        return True

def convert_str_to_arr(str_arr):
        print ('str_arr: ' + str(str_arr))
        return str_arr[0][0].replace('[', '').replace(']', '').replace('\'', '').split(',')
    
def get_state(flat_tree, nlp_output_arr):
        final_array = convert_str_to_arr(nlp_output_arr)
        for ele in flat_tree:
            if is_equal_arr(ele['path'], final_array):
                return ele['id']
        return None

def is_negation_present(sent):
    for item in sent['collapsed-ccprocessed-dependencies']:
        if item['dep'] in possibleNegTags:
            return True
    for item in sent['tokens']:
        if item['lemma'] in possible_negative_words:
            return True
    return False

def is_answer_yes(user_input):
    output = nlp.annotate(user_input, properties={'annotators': 'tokenize,ssplit,pos,lemma,depparse','outputFormat': 'json'})
    return is_negation_present(output['sentences'][0]) == False

'''
1. Takes user input, does language modeling on it. Finds nouns, pronouns and negations.
2. Does a lookup in category_tree and returns the best option and confidence value

user_input: Just me, not my family
category_tree: 
{
    0: {
        'I': 2, 
        'me': 2, 
        'my': 2
    },
    1: {
        'spouse': 2,
        'wife': 2,
        'husband': 2
    },
    2: {
        'family': 2
        'children': 2
        'parents': 2
        'dependent': 2
    }
}

1. do language modeling.
2. find pronouns, nouns and their stem words (lemma)
3. assign scores to stem words:
    3.1. if the word is a subject or object: assign higher score.
    3.2. if there is negation then multiply by -1
4.  do a lookup in each category if there is a match, find sum of products.
5.  pick the category with max value.
'''
def find_category(user_input, category_tree):
    max_category = None
    max_score = None
    category_data = category_tree['data']
    if category_tree['type'] == 'boolean':
        is_yes = is_answer_yes(user_input)
        return category_data[is_yes], sys.maxsize
    else:
        noun_arr = []
        pronoun_arr = []
        adverb_arr = []
        output = nlp.annotate(user_input, properties={'annotators': 'tokenize,ssplit,pos,lemma,depparse','outputFormat': 'json'})
        for output_sent in output['sentences']:
            noun_arr = noun_arr + lang.find_nouns(output_sent)
            pronoun_arr = pronoun_arr + lang.find_pronouns(output_sent)
            adverb_arr = adverb_arr + lang.find_adverbs(output_sent)
        is_negation = is_negation_present(output['sentences'][0])
        # assign a score of 1.5 to pronoun and 2 to nouns.
        final_arr = {}
        for noun in noun_arr:
            final_arr[noun] = 2
        for adv in adverb_arr:
            final_arr[adv] = 2
        for pro in pronoun_arr:
            final_arr[pro] = 1.5
        max_score = -1
        max_category = -1
        for category in category_data:
            sum_val = 0
            word_map = category_data[category]
            for key in final_arr:
                if key in word_map:
                    sum_val += word_map[key] * final_arr[key]
            if sum_val > max_score:
                max_score = sum_val
                max_category = category
    
    return max_category, max_score

def get_nouns_objects(output):
    noun_arr = []
    adj_arr = []
    obj_arr = []
    negation_map = {}
    for output_sent in output['sentences']:
        noun_arr = noun_arr + lang.find_nouns(output_sent)
        adj_arr = adj_arr + lang.find_adjectives(output_sent)
        obj_arr = obj_arr + lang.find_objects(output_sent)
        neg_map = lang.find_negation_map(output_sent)
        if neg_map != None and len(neg_map) > 0:
            for key in neg_map:
                negation_map[key] = neg_map[key]
    return noun_arr, adj_arr, obj_arr, negation_map

def find_state_element(nouns, objects, negation_map, flat_tree):
    result = {}
    for obj in objects:
        local_result = process_one_object(obj, obj in negation_map, flat_tree)
        for path in local_result:
            if path in result:
                result[path] = result[path] + local_result[path]
            else:
                result[path] = local_result[path]
    for noun in nouns:
        local_result = process_one_object(noun, noun in negation_map, flat_tree)
        for path in local_result:
            if path in result:
                result[path] = result[path] + local_result[path]
            else:
                result[path] = local_result[path]
    result_arr = list(result.items())
    result_arr.sort(key=lambda x: x[1], reverse=True)
    return result_arr

def process_one_object(keyword, is_negation, flat_tree):
    result = {}
    for item in flat_tree:
        if keyword in item['keywords']:
            score = item['keywords'][keyword]
            path_to_add = None
            if is_negation:
                length = len(item['path'])
                last_path_ele = item['path'][length - 1]
                if last_path_ele == 'left':
                    path_to_add = item['path'][:length - 1] + ['right']
                else:
                    if last_path_ele == 'right':
                        path_to_add = item['path'][:length - 1] + ['left']
                    else:
                        raise Exception('Illegal path name: ' + str(item['path']))
            else:
                path_to_add = item['path']
            path_to_add_str = str(path_to_add)
            if path_to_add_str in result:
                result[path_to_add_str] = result[path_to_add_str] + score
            else:
                result[path_to_add_str] = score
    return result

def analyze_output(output, flat_tree):
    # check for all the nouns in the output.
    nouns, adjectives, objects, negation_map = get_nouns_objects(output)
    print ('nouns: ' + str(nouns))
    print ('adjectives: ' + str(adjectives))
    print ('objects: ' + str(objects))
    print ('negation_map: ' + str(negation_map))
    return find_state_element(nouns + adjectives, objects, negation_map, flat_tree)