"""
Defines the set of symbols used in text input to the model.
Burmese-only vocabulary for StableTTS (character-level, no G2P).
"""

# Padding
_pad = '_'

# ASCII digits (in case clean_text misses some numerals)
_ascii_digits = '0123456789'

# Basic ASCII punctuation
_ascii_punct = ".,!?'\"-:;()"

# Burmese consonants
_burmese_consonants = (
    '\u1000\u1001\u1002\u1003\u1004\u1005\u1006\u1007\u1008\u1009'
    '\u100A\u100B\u100C\u100D\u100F\u1010\u1011\u1012\u1013\u1014'
    '\u1015\u1016\u1017\u1018\u1019\u101A\u101B\u101C\u101D\u101E'
    '\u101F\u1020\u1021'
)

# Burmese independent vowels
_burmese_independent = '\u1023\u1024\u1025\u1026\u1027\u1029\u102A'

# Burmese dependent vowels & signs
_burmese_signs = (
    '\u102B\u102C\u102D\u102E\u102F\u1030\u1031\u1032'
    '\u1036\u1037\u1038\u1039\u103A'
    '\u103B\u103C\u103D\u103E\u103F'
)

# Burmese digits
_burmese_digits = '\u1040\u1041\u1042\u1043\u1044\u1045\u1046\u1047\u1048\u1049'

# Burmese punctuation
_burmese_punct = '\u104A\u104B\u104C\u104D\u104E\u104F'

# Extension marker (rare)
_burmese_ext = '\u1064'

# Export all symbols:
symbols = (
    [_pad]
    + list(_ascii_digits)
    + list(_ascii_punct)
    + list(_burmese_consonants)
    + list(_burmese_independent)
    + list(_burmese_signs)
    + list(_burmese_digits)
    + list(_burmese_punct)
    + list(_burmese_ext)
    + [' ']
)

# Special symbol ids
SPACE_ID = symbols.index(" ")
