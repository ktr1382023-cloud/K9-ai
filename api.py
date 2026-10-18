# This file imports from the installed MyanmarTTS package.
# We are overriding the local file to use the package's implementation.
try:
    from MyanmarTTS.api import StableTTSAPI
except ImportError:
    # Fallback if the package structure is different
    from myanmartts.api import StableTTSAPI
