"""Sample Cheffu recipes, in JSON format.
"""

SAMPLE_RECIPES = {
    'Magic Mushroom Powder': {
        'author': 'Michelle Tam',
        'procedure': [
            # We need a spice grinder.
            {'APPL': 'spice grinder',},

            # We need 1 oz of dried porcini mushrooms.
            {'INGR': 'mushroom'},
            {'MODI': 'porcini',},
            {'MODI': 'dried',},
            {'QMAS': {'base': 1, 'units': 'oz',},},

            # Load the mushrooms into the spice grinder.
            # 'LOAD'
            {'ADDI': None,},

            # Pulverize the mushrooms.
            # This should detect that there is a pseudo-Tool in use, as part of the Appliance!
            {'VERB': 'grind',},

            # Get a jar.
            {'VESS': 'jar',},

            # Move the Mixture in the previous System (the pulverized mushrooms from the spice
            # grinder) into the jar.
            # This will mark the spice grinder as no longer in use and remove it from the stack
            {'MOVE': None,},

            {'INGR': 'red pepper',},
            {'MODI': 'flaked',},
            {'QVOL': {'base': 1, 'units': 'Tbsp',},},

            # Add red pepper to mixture.
            {'ADDI': None,},

            {'INGR': 'thyme',},
            {'MODI': 'dried',},
            {'QVOL': {'base': 2, 'units': 'tsp',},},

            # Add thyme to mixture.
            {'ADDI': None,},

            {'INGR': 'salt',},
            {'MODI': 'kosher',},
            {'QVOL': {'base': 2, 'base_den': 3, 'units': 'cup',},},

            # Add salt to mixture.
            {'ADDI': None,},

            {'INGR': 'black pepper',},
            {'MODI': 'fresh ground',},
            {'QVOL': {'base': 1, 'units': 'tsp',},},

            # Add pepper to mixture.
            {'ADDI': None,},

            # Need a spoon to mix the spice blend.
            # Perhaps instead of asking for a specific tool, we can ask for a Tool that matches a
            # certain interface, such as 'MIXER' or 'STIRRER'?
            {'TOOL': 'spoon',},

            # Bind the spoon to be used by the next action
            # Binding an implement pushes it onto a per-bundle Tool stack
            {'BIND': None,},

            # This will use the bound spoon, and remove it from the bundle and stack (since it is a
            # Tool, not an Appliance).
            # When acting upon a bundle, Verbs will attempt these rules in order, stopping at and
            # using the first available result:
            #     1) The topmost Tool in the bundle's Tool stack; if this occurs, the Tool is popped
            #        off the stack and discarded.
            #     2) The bundle's bound Appliance; the Appliance is NOT removed or cleaned up.
            #     3) The null Tool, which is either taken to be "unspecified", or "hands".
            {'VERB': 'mix',},
        ],
    },
    'Chamomile Tea Pound Cake': {
        'author': 'María del Mar Sacasa',
        'url': 'http://www.seriouseats.com/recipes/2013/02/chamomile-pound-cake-recipe.html',
        'procedure': [
            # Put a pot of water to boil, for steeping the tea
            {'VESS': 'pot',},
            {'INGR': 'water',},
            # 'LOAD'
            {'ADDI': None,},
            {'ENVR': 'stove',},
            # The Precondition is used for ensuring Environments or Appliances are preset correctly.
            # This is mainly useful for initial steps that may require a non-trivial amount of time,
            # such as oven preheating.
            {'PREC': 'high',},
            {'PLAC': None,},
            {'VERB': 'boil',},
            # A Quantity applied to a Mixture acts as a 'crop' of sorts
            {'QVOL': {'base': 5, 'base_den': 4, 'units': 'cup',},},

            # At this point, the stack looks like
            #     B -   pot of 1_1/4 cup boiled water

            # Add some chamomile tea bags to a bowl
            {'VESS': 'bowl',},
            {'INGR': 'chamomile tea',},
            {'QCNT': {'base': 16, 'units': 'bag',},},
            # 'LOAD'
            {'ADDI': None,},

            # At this point, the stack looks like
            #     T -   bowl of chamomile tea
            #     B -   pot of 1_1/4 cup boiled water

            {'MOVE': None,},
            {'VERB': 'steep',},
            # The Time token modifies a Verb, indicating how long to do that Verb for
            {'TIME': {'base': 8, 'range': 2, 'units': 'min',},},

            # At this point, the stack looks like
            #     B -   bowl of steeped chamomile tea (with leaves)

            # Strain the tea.
            # The Pseudo command "selects" a user-described food portion of the last bundle,
            # and makes a reference to it on the stack.
            # [[START OLD]]
            # This does NOT actually physically separate the portion from its source
            # (see below how to do that)!
            # Performing a Verb on the reference modifies that portion in-place where it was found.
            # Performing a Discard on the reference removes it from its source AND from the stack.
            # If discarding is not desired, the reference can be re-integrated with a Push
            # (which only works on references).
            # In addition, a reference can be physically separated from its souce using a Move,
            # Transfer, or Add (into a new Mixture).
            # [[CLOSE OLD]]
            {'PSEU': 'used tea',},
            {'VERB': 'strain',},
            # While straining the tea, squeeze it to release extra liquid
            # The Simultaneous token must follow a Verb, Load, or Add token, and indicates another
            # Verb action that should be done simultanouesly with the former.
            {'SIMU': 'squeeze',},
            # [[START OLD]]
            # If we wanted to keep using the tea bags for some reason, we could do a Push or
            # Move/Transfer/Add instead of a Discard.
            # [[CLOSE OLD]]
            {'DISC': None,},

            # At this point, the stack looks like
            #     B -   bowl of strained chamomile tea

            # Cool the tea by placing it at room temperature
            {'ENVR': 'room temperature',},

            # Tag the bowl of steeped tea, so that we can retrieve it later
            # Tag-Set attaches a string ID tag to a bundle, so that it can be retrieved later
            {'TSET': 'GLAZE_TEA',},

            # Divide the tea mixture in two
            # The Divide token splits a Mixture in two, based on a fraction
            # The 'keep' argument represents the part to leave behind,
            # and the 'pass' is the amount to pull out.
            # Both must be greater than 0.
            # [[START OLD]]
            # Similar to Pseudo, the Divided pass-portion is kept as a reference until it needs to
            # be separated.
            # [[CLOSE OLD]]
            {'DIVI': {'keep': 1, 'pass': 1,},},

            # At this point, the stack looks like
            #     T -   strained chamomile tea [1/2]
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # We now need to split the new half of tea into thirds, and tag them
            # Idea: allow Tag-Set to use duplicate tag names!
            {'TSET': 'BATTER_TEA',},
            {'DIVI': {'keep': 1, 'pass': 2,},},
            {'TSET': 'BATTER_TEA',},
            {'DIVI': {'keep': 1, 'pass': 1,},},
            {'TSET': 'BATTER_TEA',},

            # At this point, the stack looks like
            #     T -   strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # Start preparing batter
            {'VESS': 'bowl',},
            {'MODI': 'medium',},
            {'INGR': 'flour',},
            {'MODI': 'all-purpose',},
            {'QVOL': {'base': 2, 'units': 'cup',},},
            # 'LOAD'
            {'ADDI': None,},

            {'INGR': 'baking powder',},
            {'QVOL': {'base': 1, 'units': 'Tbsp',},},
            {'ADDI': None,},

            {'INGR': 'salt',},
            {'QVOL': {'base': 3, 'base_den': 4, 'units': 'tsp',},},
            {'ADDI': None,},
            {'TOOL': 'spoon',},
            {'BIND': None,},
            {'VERB': 'mix',},

            # At this point, the stack looks like
            #     T -   medium bowl of flour mixture
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # Split the flour mixture into three portions
            {'TSET': 'FLOUR_MIXTURE',},
            {'DIVI': {'keep': 1, 'pass': 2,},},
            {'TSET': 'FLOUR_MIXTURE',},
            {'DIVI': {'keep': 1, 'pass': 1,},},
            {'TSET': 'FLOUR_MIXTURE',},

            # At this point, the stack looks like
            #     T -   flour mixture [1/3] <FLOUR_MIXTURE>
            #           flour mixture [1/3] <FLOUR_MIXTURE>
            #           medium bowl of flour mixture [1/3] <FLOUR_MIXTURE>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            {'APPL': 'stand mixer',},
            {'INGR': 'butter',},
            {'MODI': 'unsalted',},
            {'QCNT': {'base': 5, 'base_den': 2, 'units': 'stick',},},
            # 'LOAD'
            {'ADDI': None,},

            {'INGR': 'sugar',},
            {'MODI': 'granulated',},
            {'QVOL': {'base': 3, 'base_den': 2, 'units': 'cup',},},
            {'ADDI': None,},

            {'INGR': 'lemon',},
            {'TOOL': 'zester',},
            {'BIND': None,},
            # This Verb actually "splits" the lemon into two components: the zest and the fruit.
            # Right now, we assume that the 'zest' Verb turns the entire lemon into a pile of zest.
            # Is there a better way to represent this when we'd want to use the zest AND the fruit?
            {'VERB': 'zest',},
            {'QVOL': {'base': 2, 'units': 'tsp',},},
            {'ADDI': None,},

            # The Configure token is used on Appliances and Tools in order to indicate settings
            {'CONF': 'medium speed',},
            {'VERB': 'beat',},
            {'TIME': {'base': 2, 'units': 'min',},},
            # The Until token gives an alternate stopping condition instead of/in addition to Time.
            {'UNTL': 'light and fluffy',},

            # The For-Count token executes a Group multiple times sequentially
            [
                {'INGR': 'egg',},
                {'MODI': 'large',},
                {'QCNT': {'base': 1, 'units': 'whole',},},
                {'ADDI': None,},
                {'SIMU': 'beat',},
                {'MODI', 'well',},
            ],
            {'FORC': 6,},

            # At this point, the stack looks like
            #     T -   mixer with butter/sugar/egg mixture
            #           flour mixture [1/3] <FLOUR_MIXTURE>
            #           flour mixture [1/3] <FLOUR_MIXTURE>
            #           medium bowl of flour mixture [1/3] <FLOUR_MIXTURE>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #           strained chamomile tea [1/6] <BATTER_TEA>
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            {'CONF': 'low speed',},

            # Add the flour mixture and reserved tea, in three installments each,
            # alternating between flour and tea.
            [
                {'TGET': 'FLOUR_MIXTURE',},
                {'ADDI': None,},
                {'VERB': 'mix',},
                {'TGET': 'BATTER_TEA',},
                {'ADDI': None,},
                {'VERB': 'mix',},
            ],
            {'FORC': 3,},

            {'TOOL': 'spatula',},
            {'MODI': 'rubber',},
            {'BIND': None,},
            {'VERB': 'scrape sides',},
            {'ANNO': 'as needed',},

            {'INGR': 'vanilla extract',},
            {'MODI': 'pure',},
            {'QVOL': {'base': 2, 'units': 'tsp',},},
            {'ADDI': None,},
            {'VERB': 'beat',},
            {'ANNO': 'just to combine',},

            # At this point, the stack looks like
            #     T -   mixer with batter
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # Obtain a loaf pan, and grease it lightly
            {'VESS': 'loaf pan',},
            {'DIMS': {'x': 9, 'y': 5, 'units': 'inch',},},
            {'INGR': 'baking spray',},
            # 'LOAD'
            {'ADDI': 'spray',},
            {'MODI': 'lightly',},

            # At this point, the stack looks like
            #     T -   greased loaf pan
            #           mixer with batter
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # Move the batter into the loaf pan
            {'MOVE': None,},

            # Preheat oven and bake
            {'ENVR': 'oven',},
            {'PREC': 'adjust rack',},
            {'MODI': 'middle',},
            {'PREC': 'preheat',},
            {'MODI': '350 degrees F',},
            {'PLAC': None,},
            {'VERB': 'bake',},
            {'TIME': {'base': 50, 'range': 10, 'units': 'min',},},
            # TODO: Cleaner way of handling this? Maybe a way to indicate a test?
            {'UNTL': 'tester comes out clean when inserted',},

            # Remove the cake from the oven, cool, invert onto cooling rack, and allow to fully cool
            {'REMO': None,},
            {'VERB': 'cool',},
            {'TIME': {'base': 15, 'units': 'min',},},
            {'VESS': 'cooling rack',},
            {'MOVE': 'invert onto',},
            {'VERB': 'cool',},
            {'TIME': {'base': 60, 'more_ok': True, 'units': 'min',},},
            {'UNTL': 'completely cool',},

            {'TOOL': 'skewer',},
            {'BIND': None,},
            {'VERB': 'poke holes',},

            # At this point, the stack looks like
            #     T -   completed cake
            #     B -   bowl of strained chamomile tea [1/2] <GLAZE_TEA>

            # Make the honey chamomile glaze
            {'VESS': 'saucepan',},
            {'MODI': 'small',},
            {'INGR': 'honey',},
            {'QVOL': {'base': 1, 'base_den': 3, 'units': 'cup',},},
            # 'LOAD'
            {'ADDI': None,},

            {'TGET': 'GLAZE_TEA',},
            {'ADDI': None,},

            {'ENVR': 'stove',},
            {'PREC': 'medium',},
            {'PLAC': None,},

            {'VERB': 'simmer',},
            {'UNTL': 'homogenous',},

            {'REMO': None,},
            {'VERB': 'cool',},
            {'TIME': {'base': 5, 'units': 'min',},},

            # At this point, the stack looks like
            #     T -   honey glaze
            #     B -   completed cake

            {'ADDI': 'pour over',},

            # DONE!
        ],
    },
    '': {
        'author': 'J. Kenji López-Alt',
        'url': 'http://www.seriouseats.com/recipes/2017/02/easy-creamy-mushroom-soup-quick.html',
        'procedure': [
            {'INGR': 'butter',},
            {'MODI': 'unsalted',},
            {'QVOL': {'base': 4, 'units': 'Tbsp',},},

            {'VESS': 'cutting board',},
            {'INGR': 'mushroom',},
            {'MODI': 'mixed',},
            {'EXPL': 'button, cremini, portabello, or shiitake',},
            {'QMAS': {'base': 2, 'units': 'lb',},},
            {'VERB': 'wash',},
            {'VERB': 'drain',},
            # 'LOAD'
            {'ADDI': None,},
            {'TOOL': "chef's knife",},
            {'BIND': None,},
            {'VERB': 'slice',},

            {'INGR': 'salt',},
            {'MODI': 'kosher',},

            {'INGR': 'black pepper',},
            {'MODI': 'fresh ground',},

            {'VESS': 'cutting board',},
            {'INGR': 'onion',},
            {'MODI': 'medium',},
            {'QCNT': {'base': 1, 'units': 'whole',},},
            {'VERB': 'peel',},
            # 'LOAD'
            {'ADDI': None,},
            {'TOOL': "chef's knife",},
            {'BIND': None,},
            {'VERB': 'slice',},

            {'VESS': 'cutting board',},
            {'INGR': 'garlic',},
            {'MODI': 'medium',},
            {'QCNT': {'base': 4, 'units': 'clove',},},
            {'VERB': 'peel',},
            # 'LOAD'
            {'ADDI': None,},
            {'TOOL': "chef's knife",},
            {'BIND': None,},
            {'VERB': 'slice',},

            {'INGR': 'flour',},
            {'QVOL': {'base': 2, 'units': 'Tbsp',},},

            [
                {'INGR': 'sherry',},
                {'MODI': 'dry',},
            ],
            [
                {'INGR': 'wine',},
                {'MODI': 'white',},
            ],
            {'OROP': None,},
            {'QVOL': {'base': 1, 'units': 'cup',},},

            {'INGR': 'milk',},
            {'MODI': 'whole',},
            {'QVOL': {'base': 1, 'units': 'cup',},},

            {'INGR': 'chicken stock',},
            [
                {'MODI': 'homemade',},
            ],
            [
                {'MODI': 'store-bought',},
                {'MODI': 'low-sodium',},
            ],
            {'OROP': None,},
            {'QVOL': {'base': 1, 'units': 'cup',},},

            {'INGR': 'bay laurel',},
            {'QCNT': {'base': 2, 'units': 'leaf',},},

            {'INGR': 'thyme',},
            {'MODI': 'fresh',},
            {'QCNT': {'base': 2, 'units': 'sprig',},},

            [],
            [
                {'INGR': 'lemon juice',},
            ],
            {'OROP': None,},

            {'INGR': 'assorted herbs',},
            {'MODI': 'fresh',},

            {'INGR': 'olive oil',},
            {'MODI': 'extra-virgin',},
        ],
    },
    'Batch-Muddled Mojitos': {
        'author': 'Matthew Card',
        'url': 'https://www.177milkstreet.com/recipes/batch-muddled-mojitos',
        'procedure': [
            {'APPL': 'stand mixer'},
            {'CONF': 'paddle attachment'},

            {'INGR': 'lime'},
            {'QCNT': {'base': 7, 'units': 'whole'}},
            {'VERB': 'chop'},
            {'MODI': 'coarsely'},
            {'USIN': "chef's knife"},

            # At this point, both of the inputs to this Add are eagerly evaluated.
            {'ADDI': None},

            {'INGR': 'mint'},
            {'MODI': 'fresh'},
            {'MODI': 'leaves'},
            {'QVOL': {'base': 4, 'units': 'cup'}},

            {'ADDI': None},

            {'INGR': 'sugar'},
            {'MODI': 'white'},
            {'QVOL': {'base': 3, 'base_den': 4, 'units': 'cup'}},

            {'ADDI': None},

            {'INGR': 'salt',},
            {'MODI': 'kosher'},

            {'ADDI': None},

            {'CONF': 'low'},
            {'VERB': 'mix'},
            {'UNTL': 'juice released'},
            {'UNTL': 'fragrant'},
            {'UNTL': 'syrupy'},
            {'TIME': {'base': 1, 'range': 1, 'range_den': 2, 'units': 'min'}},

            {'DIVI': None},
            {'PSEU': 'solids'},
            {'TOOL': 'strainer'},
            # The Using keyword is used to show that a Tool is to be used for a Verb or Add/Move.
            {'USIN': None},

            {'SIMU': 'press'},
            {'TOOL': 'spoon'},
            {'MODI': 'wooden'},
            {'USIN': None},

            {'VESS': 'bowl'},
            {'MODI': 'medium'},

            {'INGR': 'rum'},
            {'MODI': 'white'},
            {'QVOL': {'base': 16, 'units': 'fl oz'}},

            {'INGR': 'ice'},

            {'INGR': 'water'},
            {'MODI': 'carbonated'},
        ],
    },
}
