from . import defs

def get_keyword_from_token_dict(token_dict):
    return token_dict.keys()[0]

def is_valid(token_dict_list):
    '''Checks to see if a list of Cheffu token dicts is a valid recipe.
    '''
    stack = []

    for token_dict in token_dict_list:
        keyword = get_keyword_from_token_dict(token_dict)

        token_def = defs.TokenKeywordToDefinition[keyword]
        inputs = token_def.inputs
        arguments = token_def.arguments

        # Pop expected inputs from stack
        # Needs to be done in reverse order, because of stack LIFO-ness
        for input_ in reversed(inputs):
            i = stack.pop()
