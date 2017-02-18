DEFINITIONS = [
  {
    'name': 'Ingredient',
    'keyword': 'INGR',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'name',
      },
    ],
    'outputs': [
      'Ingredient',
    ],
    'description': 'Specifies an Ingredient to use in the recipe.',
  },
  {
    'name': 'Implement',
    'keyword': 'IMPL',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'name',
      },
    ],
    'outputs': [
      'Implement',
    ],
    'description': 'Specifies an Implement (a tool) to use in recipe actions. Implements are used to perform actions, denoted as Verbs.',
  },
  {
    'name': 'Vessel',
    'keyword': 'VESS',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'name',
      },
    ],
    'outputs': [
      'Vessel',
    ],
    'description': 'Specifies a Vessel (a container) to use for holding Ingredients and Mixtures.',
  },
  {
    'name': 'Appliance',
    'keyword': 'APPL',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'name',
      },
    ],
    'outputs': [
      'Appliance',
    ],
    'description': 'Specifies an Appliance (a combination of a Vessel and an Implement). Usually, these are electric applicances, such as blenders, electric pressure cookers, spice grinders, etc.',
  },
  {
    'name': 'Environment',
    'keyword': 'ENVR',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'name',
      },
    ],
    'outputs': [
      'Environment',
    ],
    'description': 'Specifies an Environment (an isolated location to place a System in). Usually, these are temperature-based, such as ovens, refrigerators, and light-shielded pantries.',
  },
  {
    'name': 'Configure',
    'keyword': 'CONF',
    'inputs': [
      {
        'type': 'Appliance',
        'name': 'appl',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'inst',
      },
    ],
    'outputs': [
      'Appliance',
    ],
    'description': 'Configures an Appliance for use according to {inst}, typically preheating an oven, or ensuring a refrigerator is cold enough.',
  },
  {
    'name': 'Divide',
    'keyword': 'DIVI',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt',
      },
    ],
    'arguments': [
      {
        'type': 'fraction',
        'name': 'frac',
      },
    ],
    'outputs': [
      '~Mixture',
      'Mixture',
    ],
    'description': 'Divides a Mixture into two fractional portions, as specified by {frac}. The split-off {frac} portion is returned as a bare Mixture at the top of the stack, while the remaining ~Mixture is underneath, in the same bundle it was found in.',
  },
  {
    'name': 'Meld',
    'keyword': 'MELD',
    'inputs': [
      {
        'type': '~Vessel',
        'name': 'vess',
      },
      {
        'type': 'Implement',
        'name': 'impl',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'inst',
      },
    ],
    'outputs': [
      '~Vessel + Implement',
    ],
    'description': 'Combines a Vessel and an Implement, according to {inst}. This is useful, for example, for wrapping a bowl in foil, or attaching a thermometer to a pot.',
  },
  {
    'name': 'Move',
    'keyword': 'MOVE',
    'inputs': [
      {
        'type': 'Mixture + ~Vessel',
        'name': 'mixt + ',
      },
      {
        'type': '~Vessel',
        'name': 'vess',
      },
    ],
    'arguments': [],
    'outputs': [
      'Mixture + ~Vessel',
    ],
    'description': 'Moves a Mixture from a Vessel bundle to another Vessel bundle. The old Vessel bundle is discarded from the stack.',
  },
  {
    'name': 'Place',
    'keyword': 'PLAC',
  },
  {
    'name': 'Reserve',
    'keyword': 'RESV',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt',
      },
    ],
    'arguments': [
      {
        'type': 'quantity',
        'name': 'qnty',
      },
    ],
    'outputs': [
      '~Mixture',
      'Mixture',
    ],
    'description': 'Divides a Mixture into two portions based on a quantity, as specified by {qnty}. The split-off {qnty} portion is returned as a bare Mixture at the top of the stack, while the remaining ~Mixture is underneath, in the same bundle it was found in.',
  },
  {
    'name': 'Separate',
    'keyword': 'SEPR',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt',
      },
    ],
    'arguments': [
      {
        'type': 'pseudoingredient',
        'name': 'pseu',
      },
    ],
    'outputs': [
      '~Mixture',
      'Mixture',
    ],
    'description': 'Divides a Mixture into two portions based on a pseudoingredient, as specified by {pseu}. The split-off {pseu} portion is returned as a bare Mixture at the top of the stack, while the remaining ~Mixture is underneath, in the same bundle it was found in.',
  },
  {
    'name': 'Transfer',
    'keyword': 'TRNS',
    'inputs': [
      {
        'type': 'Mixture + ~Vessel',
        'name': 'mixt + vess_a',
      },
      {
        'type': '~Vessel',
        'name': 'vess_b',
      },
    ],
    'arguments': [],
    'outputs': [
      '~Vessel',
      'Mixture + ~Vessel',
    ],
    'description': 'Moves a Mixture from a Vessel bundle to another Vessel bundle. The old Vessel bundle remains on the stack.',
  },
  {
    'name': 'Using',
    'keyword': 'USIN',
    'inputs': [
      {
        'type': 'Verb',
        'name': 'verb',
      },
      {
        'type': 'Implement',
        'name': 'impl',
      },
    ],
    'arguments': [],
    'outputs': [
      'Verb + Implement',
    ],
    'description': 'Binds an Implement to a Verb, indicating that {impl} is to be used for the {verb} action.',
  },
  {
    'name': 'Verb',
    'keyword': 'VERB',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'inst',
      },
    ],
    'outputs': [
      'Mixture',
    ],
    'description': 'Specifies an action to perform on a Mixture bundle. Returns the modified Mixture, in the same bundle it was found in.',
    'todo': [
      'Need a variant for performing actions on Vessels.',
      'Need a variant for performing actions on Implements.',
      'Need a variant for performing actions on Environments.',
    ],
  },
  {
    'name': 'Add',
    'keyword': 'ADDI',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt_a',
      },
      {
        'type': 'Mixture',
        'name': 'mixt_b',
      },
    ],
    'arguments': [],
    'outputs': [
      '~Mixture',
    ],
    'description': 'Combines a Mixture into a Mixture bundle ({mixt_b} into {mixt_a}). If {mixt_b} is part of a bundle, the remaining portions of the bundle are discarded.',
  },
  {
    'name': 'Discard',
    'keyword': 'DISC',
    'inputs': [
      {
        'type': '~Mixture',
        'name': 'mixt',
      },
    ],
    'arguments': [],
    'outputs': [],
    'description': 'Removes an entire Mixture bundle from the stack.',
  },
  {
    'name': 'Empty',
    'keyword': 'EMPT',
    'inputs': [
      {
        'type': 'Mixture + ~Vessel',
        'name': 'mixt + vess',
      },
    ],
    'arguments': [],
    'outputs': [
      '~Vessel',
    ],
    'description': 'Empties out the Mixture from a Vessel bundle, leaving the Vessel bundle on the stack.',
  },
  {
    'name': 'Precondition',
    'keyword': 'PREC',
    'inputs': [
      {
        'type': 'Environment',
        'name': 'envr',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'inst',
      },
    ],
    'outputs': [
      'Environment',
    ],
    'description': 'Specifies a setting or advance preparation for an Environment, such as preheating an oven.',
  },
  {
    'name': 'Modifier',
    'keyword': 'MODI',
    'inputs': [
      {
        'type': '~Modifiable',
        'name': 'item',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'modi',
      },
    ],
    'outputs': [
      '~Modifiable',
    ],
    'description': 'Attaches a Modifier to a Modifiable bundle on the stack. Modifiers are meant for adding important and/or critical adjectives to items on the stack.',
  },
  {
    'name': 'Annotation',
    'keyword': 'ANNO',
    'inputs': [
      {
        'type': '~Annotatable',
        'name': 'item',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'anno',
      },
    ],
    'outputs': [
      '~Annotatable',
    ],
    'description': 'Attaches an Annotation to an Annotatable bundle on the stack. Annotations are meant for adding non-critical commentary or suggestions to items on the stack.',
  },
  {
    'name': 'Photo',
    'keyword': 'PHOT',
    'inputs': [
      {
        'type': '~Photoable',
        'name': 'item',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'path',
      },
    ],
    'outputs': [
      '~Photoable',
    ],
    'description': 'Attaches a photo reference to a Photoable bundle on the stack.'
  },
  {
    'name': 'Tag-Set',
    'keyword': 'TSET',
    'inputs': [
      {
        'type': '~Taggable',
        'name': 'item',
      },
    ],
    'arguments': [
      {
        'type': 'string',
        'name': 'tag_name',
      },
    ],
    'outputs': [
      '~Taggable',
    ],
    'description': 'Attaches a callback tag to a Taggable bundle on the stack. A tagged bundle can then be called to the top of the stack using a Tag-Get. The value of {tag_name} must be unique within a recipe, reusing a {tag_name} will result in an error.',
  },
  {
    'name': 'Tag-Get',
    'keyword': 'TGET',
    'inputs': [],
    'arguments': [
      {
        'type': 'string',
        'name': 'tag_name',
      },
    ],
    'outputs': [],
    'description': 'Finds a bundle located anywhere in the stack that was tagged with {tag_name}, using Tag-Set. If found, the bundle will be moved to the top of the stack. If no bundles are found with a matching {tag_name}, an error is thrown.',
  },
]
