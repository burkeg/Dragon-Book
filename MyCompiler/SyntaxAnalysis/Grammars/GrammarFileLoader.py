import copy
import os

from BaseGrammar import BaseGrammar


class GrammarFileLoader:
    _grammar_dict = dict()

    @classmethod
    def load(cls, name):
        if len(cls._grammar_dict) == 0:
            cls._init_grammar_dict()
        if name in cls._grammar_dict:
            grammar = cls._grammar_dict[name]
        else:
            raise Exception('Unknown textbook grammar')
        return copy.copy(grammar)

    @classmethod
    def _init_grammar_file_dict(cls):
        grammar_file_dir = r'SyntaxAnalysis/Grammar Files'
        for file in os.listdir(grammar_file_dir):
            if file.endswith('.gmr'):
                with open(os.path.join(grammar_file_dir, file), mode='r', encoding='utf-8') as f:
                    cls._grammar_dict[file[:-4]] = BaseGrammar.from_string(''.join(f.readlines()))

    @classmethod
    def _init_grammar_dict(cls):
        cls._init_grammar_file_dict()

        cls._grammar_dict['4.20'] = cls._grammar_dict['4.18'].without_left_recursion()
        cls._grammar_dict['4.24'] = cls._grammar_dict['4.23'].left_factored()
        cls._grammar_dict['ANSI C refactored'] = cls._grammar_dict['ANSI C'].without_left_recursion()
        cls._grammar_dict['ANSI C refactored2'] = cls._grammar_dict['ANSI C refactored'].left_factored()



def do_stuff():
    g = GrammarFileLoader.load('ANSI C refactored2')
    print(g)

if __name__ == '__main__':
    do_stuff()