from pycorenlp import StanfordCoreNLP
import json
import sys

nlp = None

possibleNounTags = ['NN', 'NNP', 'NNS', 'NNPS']
possibleAdjTags = ['JJ', 'JJR', 'JJS', 'RB', 'RBS', 'RBR']
possibleVerbTags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
possibleObjectTags = ['obj', 'nobj', 'dobj']
possibleNegTags = ['neg']
possiblePronounTags = ['PRP']
possibleAdverbs = ['RB', 'RBR', 'RBS']

def load_model_files():
    global nlp
    nlp = StanfordCoreNLP('http://localhost:9000')
    
def is_model_loaded():
    return proc != None

def find_nouns(processed):
    nouns = []
    for token in processed['tokens']:
        if token['pos'] in possibleNounTags:
            nouns.append(token['lemma'])
    return nouns

def find_pronouns(processed):
    nouns = []
    for token in processed['tokens']:
        if token['pos'] in possiblePronounTags:
            nouns.append(token['lemma'])
    return nouns

def find_adverbs(processed):
    nouns = []
    for token in processed['tokens']:
        if token['pos'] in possibleAdverbs:
            nouns.append(token['lemma'])
    return nouns

def find_adjectives(processed):
    adjectives = []
    for token in processed['tokens']:
        if token['pos'] in possibleAdjTags:
            adjectives.append(token['lemma'])
    return adjectives
  
def find_verbs(processed):
    adjectives = []
    for token in processed['tokens']:
        if token['pos'] in possibleVerbTags:
            adjectives.append(token['lemma'])
    return adjectives

def find_objects(processed):
    objects = []
    for dep in processed['collapsed-ccprocessed-dependencies']:
        if dep['dep'] in possibleObjectTags:
            objects.append(dep['dependentGloss'])
    return objects

def find_object_same_governor(processed_arr, governer_index):
    for item in processed_arr:
        if item['dep'] in possibleObjectTags and item['governor'] == governer_index:
            return item
    return None
            

def find_negation_map(processed):
    negation_map = {}
    for dep in processed['collapsed-ccprocessed-dependencies']:
        if dep['dep'] in possibleNegTags:
            governer_index = dep['governor']
            ob_same_governer = find_object_same_governor(processed['collapsed-ccprocessed-dependencies'], governer_index)
            assert(ob_same_governer != None)
            negation_map[ob_same_governer['dependentGloss']] = True
    return negation_map

def find_sub_obj(processed):
    deps = processed['sentences'][0]['collapsed-ccprocessed-dependencies']
    subj_details = None
    obj_details = None
    mod_details = None
    for val in deps:
        if 'subj' in val['dep']:
            subj_details = val
        if 'obj' in val['dep']:
            obj_details = val
        if 'mod' in val['dep']:
            mod_details = val
    print ('details: ' + str(subj_details) + ' ; ' + str(obj_details) + ' ; ' + str(mod_details))
    #pos_tags = parsed_c['sentences'][0]['pos']
    tokens = processed['sentences'][0]['tokens']
    print('tokens: ' + str(tokens))
    obj = None
    if obj_details == None:
        if mod_details != None:
            index = mod_details['dependent'] - 1
            print('index: ' + str(index))
            obj = tokens[index]['word']
    else:
        obj = tokens[obj_details['dependent'] - 1]['word']
    sub = None
    if subj_details is not None:
        sub = tokens[subj_details['dependent'] - 1]['word']
    return sub, obj

'''
assume user input is just 1 sentence.
annotate the user input.
find object, subject and nouns, verbs, adjectives.
assign weights to these words.
at any node do keyword lookup at both left and right.
    1. 
'''

def find_attribute_2(attribute_seed, user_input, phrase_parsing=False):
    assert(is_model_loaded())
    processed = nlp.annotate(user_input, properties={'annotators': 'tokenize,ssplit,parse,pos,depparse,lemma','outputFormat': 'json'})
    