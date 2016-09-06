import unittest
import sys

sys.path.insert(0, 'scripts/binary_tree')
import language_utils as lang

class TestLanguageUtils(unittest.TestCase):
    
    def test_case(self):
        user_input = 'I share'
        category_tree = {
                'type': 'free',
                'data': {
                    0: {
                        'share': 2
                    },
                    1: {
                        'entirely': 2,
                        'entire': 2,
                        'all': 2
                    }
                }
            }
        max_category, max_score = lang.find_category(user_input, category_tree)
        print(str(max_score) + ' ; ' + str(max_category))
        assert(max_category != None)
        assert(max_category == 0)
        
    def test_case_2(self):
        user_input = 'I pay entirely'
        category_tree = {
                'type': 'free',
                'data': {
                    0: {
                        'share': 2
                    },
                    1: {
                        'entirely': 2,
                        'entire': 2,
                        'all': 2
                    }
                }
            }
        max_category, max_score = lang.find_category(user_input, category_tree)
        print(str(max_score) + ' ; ' + str(max_category))
        assert(max_category != None)
        assert(max_category == 1)
        
    def test_case_3(self):
        user_input = 'I have bills'
        category_tree = {
                'type': 'free',
                'data': {
                    0: {
                        'spend': -1
                    },
                    1: {
                        'spend': 1,
                        'bill': -1
                    },
                    2: {
                        'spend': 1,
                        'bill': 1
                    }
                }
            }
        max_category, max_score = lang.find_category(user_input, category_tree)
        print(str(max_score) + ' ; ' + str(max_category))
        assert(max_category != None)
        assert(max_category == 2)
        
    def test_case_4(self):
        user_input = 'I do not have bills'
        category_tree = {
                'type': 'free',
                'data': {
                    0: {
                        'spend': -1
                    },
                    1: {
                        'spend': 1,
                        'bill': -1
                    },
                    2: {
                        'spend': 1,
                        'bill': 1
                    }
                }
            }
        max_category, max_score = lang.find_category(user_input, category_tree)
        print(str(max_score) + ' ; ' + str(max_category))
        assert(max_category != None)
        assert(max_category == 1)
        
    def test_case_5(self):
        user_input = 'I did not spend'
        category_tree = {
                'type': 'free',
                'data': {
                    0: {
                        'spend': -1
                    },
                    1: {
                        'spend': 1,
                        'bill': -1
                    },
                    2: {
                        'spend': 1,
                        'bill': 1
                    }
                }
            }
        max_category, max_score = lang.find_category(user_input, category_tree)
        print(str(max_score) + ' ; ' + str(max_category))
        assert(max_category != None)
        assert(max_category == 0)
        
if __name__ == '__main__':
    unittest.main()