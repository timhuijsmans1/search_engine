from spellchecker import SpellChecker

spell = SpellChecker()

misspelled = spell.unknown(['something', 'is', 'finaence', 'stokc'])

for word in misspelled:
    print(spell.correction(word)) # correction returns the most likely word

    print(spell.candidates(word)) # candidates returns a list of possible alternatives