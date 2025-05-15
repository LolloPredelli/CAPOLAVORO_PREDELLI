
##########################################################################################################
#                                                                                                        #
#                                           MAIND MAP PROJECT                                            #
#                                          by Lorenzo Predelli                                           #
#                                  capolavoro di maturità (A.S. 2024/25)                                 #
#                                                                                                        #
##########################################################################################################



##########################################################################################################
#                                            BUILD ENVIROMENT                                            #
##########################################################################################################

# import dependencies
import spacy
from spacy.tokens import Doc
import pytextrank
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import re
import json

# constants
TEXT_URL = "develop/Backend/modules/texts/text.txt"
LANGUAGE_MODEL = "en_core_web_lg"
INPUT_TEXT = ""
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
        'appos' : 'BLOCK',
        'mark' : 'LINK',
        'advcl' : 'LINK',
        'relcl' : 'LINK',
        'cc' : 'LINK',
        'prep' : 'LINK',
        'punct' : 'HIDE',
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

# Read input text from file
with open(TEXT_URL, "r", encoding="utf-8") as file:
    INPUT_TEXT = file.read()

# Load the spaCy language model with word vectors
nlp = spacy.load(LANGUAGE_MODEL)
print("DEBUG: Language model loaded")

# Add pyTextRank to the pipeline
nlp.add_pipe("textrank", last=True)
print("DEBUG: pyTextRank added to spaCy pipeline")

##########################################################################################################
#                                                CLASSES                                                 #
##########################################################################################################

# Class to represent an element (node or connection) in a conceptual map
class Element:
    def __init__(self, id=None, value=None, type=None, link=None, dep=None):
        self.id = id          # Unique token index
        self.value = value    # Text value of the element
        self.type = type      # Element type: BLOCK, LINK, HIDE, or UNSET
        self.link = link      # Index of the head token (link target)
        self.dep = dep        # Dependency relation (e.g., 'nsubj', 'prep')

##########################################################################################################
#                                               FUNCTIONS                                                #
##########################################################################################################

# Function to clean and process the text
def preprocess_text(text: str):
    # Remove bracketed references like [1], [12], [a], etc.
    text = re.sub(r"\[\w{1,3}\]", "", text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r"\s{2,}", " ", text)

    # Strip leading and trailing spaces and process with spaCy
    sanitized_text = text.strip()
    doc = nlp(sanitized_text)
    print("DEBUG: Text processed")
    return doc

# Function to extract key phrases and their lemmatized forms
def find_keyphrases(doc: Doc):
    keywords = list()          # List to hold keyword phrases
    lemma_keywords = list()    # List to hold lemmatized keywords

    n_keyphrases = len(list(doc.sents))  # Get one keyword per sentence

    # Extract top-ranked keyphrases using pyTextRank
    for phrase in doc._.phrases[:n_keyphrases]:
        keywords.append(phrase.text)
        for word in phrase.text.split(" "):
            for token in doc:
                # Keep alphabetic, non-stop words
                if token.text == word and token.is_alpha and not token.is_stop:
                    lemma_keywords.append(token.lemma_.lower())
    return keywords, lemma_keywords

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
            if token.dep_ in {"ROOT", "nsubj", "dobj", "nsubjpass"}:
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

# Determine the type of a token based on dependency rules and its context
def get_element_type(token, doc):
    roots = find_ent_roots(doc)  # Entity root token indices
    type = None

    # If inside a named entity but not a root, mark as UNSET
    if token.ent_iob_ == "I" and not(token.i in roots):
        type = 'UNSET'

    # Hide pronoun subjects
    if token.dep_ == 'nsubj' and token.pos_ == 'PRON':
        type = 'HIDE'

    # Special case: check if the preposition belongs to a relative clause or entity
    elif token.i > 0:
        if token.dep_ == 'prep':
            if token.head.dep_ == 'acl':
                type = 'UNSET'
            elif doc[token.i - sent.start - 1].ent_iob_ in {"B", "I"}:
                type = 'UNSET'

    # If still unset, apply rule based on dependency label
    if type == None:
        type = RULES[token.dep_]
    
    return type

# Identify the head tokens of coordinated lists (e.g., apples, oranges, and bananas)
def spot_list_heads(doc):
    list_heads = list()
    for token in doc:
        has_conj = False
        has_cc = False
        for child in list(token.children):
            if child.dep_ == "conj":
                has_conj = True
            elif child.dep_ == "cc":
                has_cc = True
        if(has_cc and has_conj):
            list_heads.append(token.i)
    return list_heads

# Build elements from sentence tokens
def build_elements(doc):
    token_to_element = {}  # Maps token.i to its Element
    token_to_type = {}     # Maps token to its assigned type

    # Step 1: Assign a type to each token
    for token in doc:
        token_to_type[token] = get_element_type(token, doc)
        #print(token.i, ": ", token.text, " - ", token.dep_ ," -> ", token_to_type[token])

    # Step 2: Build Elements based on their type
    for token in doc:
        type_ = token_to_type[token]

        if type_ == 'HIDE':
            continue  # Skip hidden elements

        if type_ == 'UNSET':
            # Climb the dependency tree to find a suitable head
            head = token.head
            while head != head.head and token_to_type.get(head, None) == 'UNSET':
                head = head.head

            # If no suitable head found, skip this token
            if head == token:
                continue

            # Append token's text to the true head's element value
            elem = token_to_element.get(head.i)
            if elem is None:
                elem = Element(id=head.i, value=token.text, type=token_to_type[head], link=head.head.i, dep=head.dep_)
                token_to_element[head.i] = elem
            else:
                elem.value += " " + token.text
        else:
            # If it's a BLOCK or LINK, create or update an Element
            elem = token_to_element.get(token.i)
            if elem is None:
                elem = Element(id=token.i, value=token.text, type=type_, link=token.head.i, dep=token.dep_)
                token_to_element[token.i] = elem
            else:
                elem.value += " " + token.text

    # Return the Elements sorted by their token index
    return [token_to_element[i] for i in sorted(token_to_element)]



##########################################################################################################
#                                                  MAIN                                                  #
##########################################################################################################

# Step 1: Process the text
doc = preprocess_text(INPUT_TEXT)

# Step 2: Find keyphrases and their lemmatized forms
keywords, lemmas = find_keyphrases(doc)

# Step 3: Identify the most relevant sentences
important_sents = find_important_sentences(doc, keywords, lemmas)

# Step 4: Generate a title from the most important content
title = find_title(important_sents, doc)

# Output the generated title and important sentences
print("\nSuggested Title:")
print(title)

print("\nImportant Sentences:")
for sent, score in important_sents:
    print(f"- {sent.text.strip()} (score: {score:.2f})")



##########################################################################################################
#                                                CREDITS                                                 #
##########################################################################################################
    
# Copyright 2025 Lorenzo Predelli. All rights reserved.
# comments made with the help of chatgpt.com
