
##########################################################################################################
#                                                                                                        #
#                                           MAIND MAP PROJECT                                            #
#                                          by Lorenzo Predelli                                           #
#                                  capolavoro di maturità (A.S. 2024/25)                                 #
#                                                                                                        #
##########################################################################################################



##########################################################################################################
#                                          VERSION UPDATEDS                                              #
##########################################################################################################

# json sanitize feature introduced 
# improved tree building feature to support lists



##########################################################################################################
#                                            BUILD ENVIROMENT                                            #
##########################################################################################################

# import dependencies
import spacy
from spacy.tokens import Doc
import pytextrank
from collections import Counter
import numpy as np
import re
#from fastapi import FastAPI, Request
from pydantic import BaseModel
import datetime

# constants
LANGUAGE_MODEL = 'en_core_web_lg'
RULES = {
        'ROOT' : 'BLOCK',
        'nsubj' : 'BLOCK',
        'pobj' : 'BLOCK',
        'dobj' : 'BLOCK',
        'ccomp' : 'BLOCK',
        'pcomp' : 'BLOCK',
        'conj' : 'BLOCK',
        'attr' : 'BLOCK',
        'npadvmod' : 'BLOCK',
        'xcomp' : 'BLOCK',
        'csubj' : 'BLOCK',
        'csubjpass' : 'BLOCK',
        'dative' : 'BLOCK',
        'oprd' : 'BLOCK',

        'mark' : 'LINK',
        'advcl' : 'LINK',
        'relcl' : 'LINK',
        'cc' : 'LINK',
        'prep' : 'LINK',
        'prt' : 'LINK',

        'punct' : 'HIDE',
        'appos' : 'HIDE',
        'intj' : 'HIDE',
        'meta' : 'HIDE',
        'discourse' : 'HIDE',
        'goeswith' : 'HIDE',
        'reparandum' : 'HIDE',

        'amod' : 'UNSET',
        'nsubjpass' : 'UNSET',
        'det' : 'UNSET',
        'nmod' : 'UNSET',
        'compound' : 'UNSET',
        'acl' : 'UNSET',
        'nummod' : 'UNSET',
        'advmod' : 'UNSET',
        'quantmod' : 'UNSET',
        'aux' : 'UNSET',
        'auxpass' : 'UNSET',
        'poss' : 'UNSET',
        'case' : 'UNSET',
        'dep' : 'UNSET'
}

# Load the spaCy language model with word vectors
nlp = spacy.load(LANGUAGE_MODEL)
print(datetime.datetime.now(), ' DEBUG: Language model loaded')

# Add pyTextRank to the pipeline
nlp.add_pipe('textrank', last=True)
print(datetime.datetime.now(), ' DEBUG: pyTextRank added to spaCy pipeline')



##########################################################################################################
#                                                CLASSES                                                 #
##########################################################################################################

# Class for the API request
class InputText(BaseModel):
    text: str


# Class to represent an element (node or connection) in a conceptual map
class Element:
    def __init__(self, id=None, type=None, link=None, dep=None, x=0, y=0):
        self.id = id          # Unique token index
        self.type = type      # Element type: BLOCK, LINK, HIDE, or UNSET
        self.link = link      # Index of the head token (link target)
        self.dep = dep        # Dependency relation (e.g., 'nsubj', 'prep') 
        self.value = []       # List of tokens' indexes
        self.children = []    # List of children
        self.coordinates = [x, y]

    def add_value(self, new_index):
        if not new_index in self.value:
            new_value = []
            added = False
            for index in self.value:
                if (new_index < index and added == False):
                    new_value.append(new_index)
                    new_value.append(index)
                    added = True
                else:
                    new_value.append(index)
            if not(new_index in new_value):
                new_value.append(new_index)

            self.value = new_value

    def add_child(self, child):
        self.children.append(child)

    def value_to_string(self, doc):
        string = ''
        for v in self.value:
            string += doc[v].text + ' '
        return string



##########################################################################################################
#                                               FUNCTIONS                                                #
##########################################################################################################

# Function to clean and process the text
def preprocess_text(text: str):
    # Remove bracketed references like [1], [12], [a], etc.
    text = re.sub(r'\[\w{1,3}\]', '', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r'\s{2,}', ' ', text)

    # Strip leading and trailing spaces and process with spaCy
    sanitized_text = text.strip()
    doc = nlp(sanitized_text)
    return doc

# Function to extract key phrases and their lemmatized forms
def find_keyphrases(doc: Doc):
    keywords = list()          # List to hold keyword phrases
    lemma_keywords = list()    # List to hold lemmatized keywords

    n_keyphrases = len(list(doc.sents))  # Get one keyword per sentence

    # Extract top-ranked keyphrases using pyTextRank
    for phrase in doc._.phrases[:n_keyphrases]:
        keywords.append(phrase.text)
        for word in phrase.text.split(' '):
            for token in doc:
                # Keep alphabetic, non-stop words
                if token.text == word and token.is_alpha and not token.is_stop:
                    lemma_keywords.append(token.lemma_.lower())
    return keywords, lemma_keywords

# Compare vectors and find similarity
def cosine_similarity(vectors):
    '''
    Compute cosine similarity matrix using numpy only.
    '''
    vectors = np.array(vectors)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    normalized = vectors / (norms + 1e-10)  # Avoid division by zero
    return np.dot(normalized, normalized.T)

# Function to identify the most relevant sentences
def find_important_sentences(doc : Doc, keywords, lemma_keywords):
    sentences = list(doc.sents)

    # Keep only sentences with valid vectors
    valid_sentences = [sent for sent in sentences if sent.vector_norm > 0]
    sentence_vectors = [sent.vector for sent in valid_sentences]

    # Compute similarity matrix between sentence vectors
    similarity_matrix = cosine_similarity(sentence_vectors)

    # Compute a base score for each sentence
    scores = similarity_matrix.sum(axis=1)

    # Apply boosts based on sentence position and keyword presence
    for i, sent in enumerate(valid_sentences):
        boost = 0

        # Boost early sentences (e.g., introduction)
        if i < len(sentences) / 10 or i == 0:
            boost += 0.4

        # Boost if the sentence contains a full keyword phrase
        for keyword in keywords:
            if keyword in sent.text:
                boost += 0.2

        # Boost if the sentence contains a keyword lemma
        for token in sent:
            if token.lemma_ in lemma_keywords:
                boost += 0.1
        
        # Apply the total boost to the score
        scores[i] = scores[i] + (scores[i] * boost)

    # Rank the sentences by score
    ranked_sentences = sorted(zip(valid_sentences, scores), key=lambda x: x[1], reverse=True)

    # Select the top sentences (at least 3 or 10% of total)
    num_sentences = max(len(ranked_sentences) // 10, 3)
    return ranked_sentences[:num_sentences]

# Function to determine a suitable title for the text
def find_title(important_sentences, doc:Doc):

    # Extract key syntactic elements from the top sentences
    main_elements = list()
    for sent in important_sentences:
        for token in sent[0]:
            if token.dep_ in {'ROOT', 'nsubj', 'dobj', 'nsubjpass'}:
                main_elements.append(token.lemma_)

    # Identify the most common main topic word
    count = Counter(main_elements)
    main_topic = count.most_common(1)[0][0]

    # Collect all noun chunks related to the main topic
    main_chunks = list()
    for chunk in doc.noun_chunks:
        for token in chunk:
            if token.lemma_ == main_topic:
                main_chunks.append(chunk.text)
    
    # Determine the most representative noun chunk as the title
    count = Counter(main_chunks)
    title = count.most_common(1)[0][0]

    return title

# Get indices of root tokens in named entities
def find_ent_roots(doc):
    roots = {ent.root.i for ent in doc.ents}
    return roots

# Return the index of the first ROOT token found in a doc
def find_root(doc):
    for token in doc:
        if token.dep_ == 'ROOT':
            return token.i 
    return False

# Return the index of the subject that serfers to the ROOT token found in a doc
def find_subject(doc):
    for token in doc:
        if(token.dep_ == 'nsubj' and token.head.i == find_root(doc)):
            return token.i
    return False

# Return the index of the parent with a type different from 'UNSET' of a given token
def find_head_with_type(token, type_array):
    head = token.head
    # print('DEBUG: ', token.text)
    # print('DEBUG: ', head.text, ' -> ', type_array[head.i], ' != ', head.head.text)
    while head != head.head and type_array[head.i] == 'UNSET':
        head = head.head

    return head.i

# Determine the type of a token based on dependency rules and its context
def get_element_type(token, doc):
    roots = find_ent_roots(doc)  # Entity root token indices
    type = None

    # If inside a named entity but not a root, mark as UNSET
    if token.ent_iob_ == 'I' and not(token.i in roots):
        type = 'UNSET'

    # Hide pronoun subjects
    if token.dep_ == 'nsubj' and token.pos_ == 'PRON':
        type = 'HIDE'

    if token.dep_ == 'cc' and token.head.dep_ == 'conj':
        type = 'HIDE'

    # Special case: check if the preposition belongs to a relative clause or entity
    elif token.i > 0:
        if token.dep_ == 'prep':
            if token.head.dep_ == 'acl':
                type = 'UNSET'
            elif doc[token.i - doc.start - 1].ent_iob_ in {'B', 'I'}:
                type = 'UNSET'

    # If still unset, apply rule based on dependency label
    if type == None:
        type = RULES[token.dep_]
    
    return type

# Identify the head tokens of coordinated lists (e.g., apples, oranges, and bananas)
def find_list_head(token, type_array):
    head = token.head
    while (head.dep_ in ['conj','cc']) or type_array[head.i] == 'UNSET':
        head = head.head  
    return head.head.i

# Build elements from sentence tokens
def build_elements(doc, current_index, element_array, type_array):
    current_token = doc[current_index]
    current_type = type_array[current_token.i]

    if current_type in ('BLOCK', 'LINK'):
        element = Element(id=current_token.i, type=current_type, dep=current_token.dep_)
        element.add_value(current_index)
        element_array[current_index] = element

        
    elif current_type == 'UNSET':
        head = current_token.head
        while head != head.head and type_array[head.i] == 'UNSET':
            head = head.head

        element_array[head.i].add_value(current_index)
    
    # Process children
    for child in current_token.children:
        build_elements(doc, child.i, element_array, type_array)

    return element_array

# Return the elements' tree structure
def link_elements_as_tree(doc, element_array, type_array, root_index, subject_index):

    # Collega ROOT al soggetto
    if root_index in element_array and subject_index in element_array:
        element_array[root_index].link = element_array[subject_index]
        element_array[subject_index].add_child(element_array[root_index])

    # Collega tutti gli altri elementi secondo il loro head
    for i, elem in element_array.items():
        if elem.id == root_index:
            continue  # Salta ROOT, già collegato
        
        # if it is a list element
        if elem.dep == 'conj':
            head_index = find_list_head(doc[i], type_array)
        else:
            head_index = find_head_with_type(doc[i], type_array)

        if head_index in element_array:
            elem.link = element_array[head_index]
            element_array[head_index].add_child(elem)

    if subject_index in element_array:
        return element_array[subject_index] 
    else:
        return element_array[root_index]

# Return the json structure of an element tree
def element_tree_to_json(doc, element, visited=None):
    if visited is None:
        visited = set()  # inizializza l'insieme dei nodi visitati

    # Se l'elemento è già stato visitato, interrompi la ricorsione
    if element.id in visited:
        return {}

    # Aggiungi l'elemento alla lista dei visitati
    visited.add(element.id)

    return {
        'id' : element.id,
        'type': element.type,
        'value': element.value_to_string(doc),
        'link': element.link.id if element.link else None,
        'dep' : element.dep,
        'coordinates' : element.coordinates,
        'children': [element_tree_to_json(doc, child, visited) for child in element.children]
    }

# Sanitize json from all the void elements and useless branches
def sanitize_json(json):
    sanitized_children = []
    for child in json['children']:
        # if element has id property (is not null)
        if 'id' in child:
            # if element is a link with something
            if not(child['type'] == 'LINK' and child['children'] == []):
                # if both child type and element type are link
                if child['type'] == 'LINK' and json['type'] == 'LINK':
                    # then join vaslue and remove child
                    json['value'] = json['value'] + child['value']
                else:    
                    # else add child
                    sanitized_children.append(child)
                    sanitize_json(child)
    json['children'] = sanitized_children
    return json



##########################################################################################################
#                                                 CREATE                                                 #
##########################################################################################################

def create(text):
    # Step 1: Process the text
    doc = preprocess_text(text)
    print(datetime.datetime.now(), ' DEBUG: Text processed')

    # Step 2: Find keyphrases and their lemmatized forms
    keywords, lemmas = find_keyphrases(doc)
    print(datetime.datetime.now(), ' DEBUG: Keyphrases found')

    # Step 3: Identify the most relevant sentences
    important_sents = find_important_sentences(doc, keywords, lemmas)
    print(datetime.datetime.now(), ' DEBUG: Keysentences found')

    # Step 4: Generate a title from the most important content
    title = find_title(important_sents, doc)
    print(datetime.datetime.now(), ' DEBUG: Title found')

    # Step 5: analyze sentences
    map_structure = {'id' : -1, 'type': 'TITLE', 'dep' : '', 'link' : '', 'value' : title, 'coordinates' : [0,0], 'children' : []}
    for sent, score in important_sents:
        root = find_root(sent)
        subj = find_subject(sent)
        type_array = {}
        for token in sent:
            type_array[token.i] = get_element_type(token, sent)
        print(datetime.datetime.now(), ' DEBUG: root, subject and tyeps found')

    # Step 5: Split sentences in logical elements
        element_dictionary = build_elements(doc, root, {}, type_array)
        print(datetime.datetime.now(), ' DEBUG: element built')

    # Step 6: Convert elements into a JSON structure
        tree_structure = link_elements_as_tree(doc, element_dictionary, type_array, root, subj)
        json_structure = element_tree_to_json(doc, tree_structure)
        map_structure['children'].append(json_structure)
        print(datetime.datetime.now(), ' DEBUG: branch JSON structure created')
        map_structure = sanitize_json(map_structure)
        print(datetime.datetime.now(), ' DEBUG: branch JSON structure sanitized')

    return map_structure



##########################################################################################################
#                                              API HANDLING                                              #
##########################################################################################################
text = """
World War II[b] or the Second World War (1 September 1939 – 2 September 1945) was a global conflict between two coalitions: the Allies and the Axis powers. Nearly all of the world's countries participated, with many nations mobilising all resources in pursuit of total war. Tanks and aircraft played major roles, enabling the strategic bombing of cities and delivery of the first and only nuclear weapons ever used in war. World War II was the deadliest conflict in history, resulting in 70 to 85 million deaths, more than half of which were civilians. Millions died in genocides, including the Holocaust, and by massacres, starvation, and disease. After the Allied victory, Germany, Austria, Japan, and Korea were occupied, and German and Japanese leaders were tried for war crimes.

The causes of World War II included unresolved tensions in the aftermath of World War I and the rises of fascism in Europe and militarism in Japan. Key events preceding the war included Japan's invasion of Manchuria in 1931, the Spanish Civil War, the outbreak of the Second Sino-Japanese War in 1937, and Germany's annexations of Austria and the Sudetenland. World War II is generally considered to have begun on 1 September 1939, when Nazi Germany, under Adolf Hitler, invaded Poland, after which the United Kingdom and France declared war on Germany. Poland was divided between Germany and the Soviet Union under the Molotov–Ribbentrop Pact. In 1940, the Soviets annexed the Baltic states and parts of Finland and Romania. After the fall of France in June 1940, the war continued mainly between Germany and the British Empire, with fighting in the Balkans, Mediterranean, and Middle East, the aerial Battle of Britain and the Blitz, and naval Battle of the Atlantic. Through campaigns and treaties, Germany gained control of much of continental Europe and formed the Axis alliance with Italy, Japan, and other countries. In June 1941, Germany led an invasion of the Soviet Union, opening the Eastern Front and initially making large territorial gains.

In December 1941, Japan attacked American and British territories in Asia and the Pacific, including at Pearl Harbor in Hawaii, leading the United States to enter the war against Japan and Germany. Japan conquered much of coastal China and Southeast Asia, but its advances in the Pacific were halted in June 1942 at the Battle of Midway. In early 1943, Axis forces were defeated in North Africa and at Stalingrad in the Soviet Union, and that year their continued defeats on the Eastern Front, an Allied invasion of Italy, and Allied offensives in the Pacific forced them into retreat on all fronts. In 1944, the Western Allies invaded France at Normandy as the Soviet Union recaptured its pre-war territory and the US crippled Japan's navy and captured key Pacific islands. The war in Europe concluded with the liberation of German-occupied territories; invasions of Germany by the Western Allies and the Soviet Union, which culminated in the fall of Berlin to Soviet troops; and Germany's unconditional surrender on 8 May 1945. On 6 and 9 August, the US dropped atomic bombs on Hiroshima and Nagasaki in Japan. Faced with an imminent Allied invasion, the prospect of further atomic bombings, and a Soviet declaration of war and invasion of Manchuria, Japan announced its unconditional surrender on 15 August, and signed a surrender document on 2 September 1945.

World War II transformed the political, economic, and social structures of the world, and established the foundation of international relations for the rest of the 20th century and into the 21st century. The United Nations was created to foster international cooperation and prevent future conflicts, with the victorious great powers—China, France, the Soviet Union, the UK, and the US—becoming the permanent members of its security council. The Soviet Union and US emerged as rival global superpowers, setting the stage for the half-century Cold War. In the wake of Europe's devastation, the influence of its great powers waned, triggering the decolonisation of Africa and Asia. Many countries whose industries had been damaged moved towards economic recovery and expansion.
"""
print(create(text))

'''
# initialize app
app = FastAPI()    

# endpoint POST
@app.post('/predict')
def predict(data: InputText):
    print(datetime.datetime.now(), " DEBUG: NEW REQUEST")
    result = create(data.text)
    return result
'''

##########################################################################################################
#                                                CREDITS                                                 #
##########################################################################################################
    
# Copyright 2025 Lorenzo Predelli. All rights reserved.
# comments made with the help of chatgpt.com