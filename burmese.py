"""
Character-level text frontend for Burmese.
No real G2P: we clean the text and pass characters through directly.
Matches the interface of english_to_ipa2 / japanese_to_ipa2 (returns a list).
"""
import re

# Burmese Unicode ranges
_BURMESE_RANGES = (
    (0x1000, 0x109F),   # Myanmar
    (0xAA60, 0xAA7F),   # Myanmar Extended-A
    (0xA9E0, 0xA9FF),   # Myanmar Extended-B
)

# Allow these through the cleaner; everything else gets dropped
_ALLOWED_ASCII_PUNCT = set(".,!?'\"-:;()")
_ALLOWED_BURMESE_PUNCT = set("\u104A\u104B\u104C\u104D\u104E\u104F")


def _is_burmese(ch):
    o = ord(ch)
    return any(lo <= o <= hi for lo, hi in _BURMESE_RANGES)


def clean_burmese(text):
    """Keep only Burmese chars, spaces, and whitelisted punctuation."""
    out = []
    for ch in text:
        if ch in (" ", "\t", "\n", "\r"):
            out.append(" ")
        elif _is_burmese(ch):
            out.append(ch)
        elif ch in _ALLOWED_ASCII_PUNCT or ch in _ALLOWED_BURMESE_PUNCT:
            out.append(ch)
        # else: drop silently
    return re.sub(r"\s+", " ", "".join(out)).strip()


def burmese_to_ipa2(text):
    """Return a list of character tokens (matches the IPA-G2P interface)."""
    cleaned = clean_burmese(text)
    return list(cleaned)
