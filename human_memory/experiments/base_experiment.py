from utils.wordlist import WORDLIST, ALL_WORDS, CATEGORIES
import random

class BaseExperiment():

    def __init__(self, category_amount: int, word_amount: int):
        self.categories = random.sample(CATEGORIES, category_amount)
        self.categorized_words = {}
        for i in self.categories:
            rand_words = random.sample(WORDLIST[i], word_amount)
            self.categorized_words[i] = rand_words
        
    def create_tuple_list(self):
        tuple_list = []
        for i in self.categorized_words:
            for j in self.categorized_words[i]:
                tuple_list.append((i, j))
        self.tuple_list = tuple_list
        tuple_list_copy = tuple_list.copy()
        random.shuffle(tuple_list_copy)
        self.shuffled_tuple_list = tuple_list_copy



