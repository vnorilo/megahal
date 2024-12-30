import sys
import json
import random
import re

empty_node = {
    "symbol": 0,
    "usage": 0,
    "count": 0,
    "branches": {}
 }

class MegaHAL:
    def __init__(self, order = 5, 
                 dictionary = ["<FIN>", "<ERROR>"], 
                 forward = empty_node, 
                 backward = empty_node):
        self.dictionary = dictionary
        self.order = order
        self.forward = forward
        self.backward = backward
        self.dictionary_lookup = self.make_lookup(dictionary)

    def make_lookup(self, dictionary):
        return {value: index for index,value in enumerate(dictionary)}

    def interpret(self, symbols):
        sentence = "".join(self.dictionary[i] for i in symbols if i>1).lower()
        return re.sub(r'([.!?]|^)(\s*[a-z])', lambda x: x.group(1) + x.group(2).upper(), sentence)

    def find_context(self, predictor, key):
        if len(key) < 1 or predictor is None:
            return predictor
        return self.find_context(predictor["branches"].get(key[0], None), key[1:])

    def pick_branch(self, predictor):
        data = predictor["branches"]
        keys = list(data.keys())
        weights = [float(data[k]["count"]) for k in keys]
        return random.choices(keys, weights=weights, k=1)[0]

    def extend(self, tokens, predictor):
        for l in range(self.order,0,-1):
            context = self.find_context(predictor, tokens[-l:])

            if context is not None and len(context["branches"]) > 0:
                choice = self.pick_branch(context)
                tokens.append(choice)
                return

        tokens.append(0)

    def extend_loop(self, tokens, predictor, limit):
        while len(tokens) < limit:
            self.extend(tokens, predictor)
            if tokens[-1] < 2:
                break

    def generate(self, tokens, limit=100):
        self.extend_loop(tokens, self.forward, limit)
        tokens.reverse()
        self.extend_loop(tokens, self.backward, limit * 2)
        tokens.reverse()
        return tokens

    def intern(self, word):
        if word in self.dictionary_lookup:
            return self.dictionary_lookup[word]

        index = len(self.dictionary)
        self.dictionary_lookup[word] = index
        self.dictionary.append(word)
        return index

    def split_tokens(self, sentence):
        return re.findall(r"\w+|\W+",sentence)

    def parse(self, sentence):
        sentence = sentence.upper()
        return [0] + [self.intern(word) for word in self.split_tokens(sentence)] + [0]

    def respond(self, sentence):

        sentence = sentence.upper()

        keywords = [self.dictionary_lookup[word] 
                    for word in self.split_tokens(sentence) 
                    if word in self.dictionary_lookup
                       and re.match(r"^\w", word)]

        if len(keywords) < 1:
            return "..."

        seed = random.choices(keywords)[0]
        return self.interpret(self.generate([seed]))


    def learn_chain(self, predictor, chain):

        if len(chain) < 2:
            return

        for link in chain:
            branches = predictor["branches"]
            
            if link not in branches:
                branches[link] = {
                    "symbol": link,
                    "usage": 0,
                    "count": 0,
                    "branches": {}
                }

            predictor["usage"] += 1
            branches[link]["count"] +=1

            predictor = branches[link]
        
        return

    def to_dict(self):
        return {
            "order": self.order,
            "forward": self.forward,
            "backward": self.backward,
            "dictionary": self.dictionary
        }

    def learn_chains(self, tokens, predictor):
        if len(tokens) < 4:
            return

        for chain in [tokens[i:i+self.order] for i in range(len(tokens))]:
            self.learn_chain(predictor, chain)

    def learn(self, sentence):
        tokens = self.parse(sentence)
        self.learn_chains(tokens, self.forward)
        self.learn_chains(list(reversed(tokens)), self.backward)