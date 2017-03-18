from defs import TokenKeywordToDef

def process_tokens(token_dicts):
    stack = []

    # Convert token dicts to token instances
    token_insts_and_defs = []
    for token_dict in token_dicts:
        # Check that there is only one key/value pair in the dict
        # Note the extra comma outside
        (token_keyword, token_argument,), = token_dict.items()

        if token_keyword not in TokenKeywordToDef:
            raise Exception()

        token_def = TokenKeywordToDef[token_keyword]

        schema = token_def.schema
        schema(token_dict)
        # token_inst = token_def.schema.deserialize(token_dict)
        # token_insts_and_defs.append((token_inst, token_def))

    # This needs to be done in a nested loop, as per the different levels of precedence
    for token_inst, token_def in token_insts_and_defs:
        inputs = []
        for input_schema in token_def.inputs:
            stack_item = stack.pop()
            # TODO: This would be a constructed class, no? Maybe just do subclass check instead
            # input_schema.validate(stack_item)
            inputs.append(stack_item)

        inputs = reversed(inputs)
        #         argument = token_value
        #
        #         dict_to_stack = {}
        #         def.argument_processor(dict_to_stack, argument)
        #         def.processor(token_dict, STACK)
