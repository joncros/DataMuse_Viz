import time

from words.models import Word, PartOfSpeech
import datamuse
import json
import logging

# Logic to read a JSON response received from DataMuse

# three letter codes used for finding words related to a word
relation_codes = [
    'jja',
    'jjb',
    'syn',
    'trg',
    'ant',
    'spc',
    'gen',
    'com',
    'par',
    'bga',
    'bgb',
    'rhy',
    'nry',
    'hom',
    'cns',
]

possible_parts_of_speech = [choice[0] for choice in PartOfSpeech.part_choices]

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Get a DataMuse instance for making queries through python-datamuse
api = datamuse.Datamuse()


def query_with_retry(retries: int, wait: float, **kwargs):
    """Datamuse query with kwargs, retry a certain number of times (wait a number of seconds in between) on failure."""
    for i in range(0, retries):
        try:
            if i > 1:
                logger.info(f'trying again: attempt {i+1} of {retries}')
            result = api.words(**kwargs)
            return result
        except ValueError:
            logger.info(ValueError)
            logger.info('DataMuse query failed.')
            time.sleep(wait)


def decode_word(dct):
    """Decodes a json response corresponding to a single word to get a Word object"""
    if dct == []:
        # raise error or log?
        pass
    else:
        word = Word.objects.get_or_create(name=dct['word'])[0]

        # update word to indicate successful DataMuse query
        word.datamuse_success = True

        # process dct['tags'], which is a dictionary that can contain frequency and part(s) of speech
        tags = dct['tags']
        for tag in tags:
            if tag in possible_parts_of_speech:
                part = PartOfSpeech.objects.get_or_create(name=tag)[0]
                logger.debug(part)
                word.parts_of_speech.add(part)
            elif tag[:2] == 'f:':
                word.frequency = float(tag[2:])

        # add definitions if present
        if 'defs' in dct:
            word.definitions = dct['defs']

        word.save()
        return word


def add_or_update_word(word: str):
    """Query DataMuse for the parts_of_speech, frequency and definitions of a Word"""
    if Word.objects.filter(name=word).exists() and Word.objects.get(name=word).datamuse_success is True:
        # word already in database and Datamuse call already successfully performed. Skip DataMuse query
        logger.debug(f'{word} values already populated from DataMuse')
        return Word.objects.get(name=word)

    # do api query, give up after 5 attempts
    result = query_with_retry(5, 1.0, sp=word, md='dpf', max=1)

    # check if result is not empty and the entry is a word that exactly matches the parameter
    if result and result[0]['word'] == word:
        # convert result to string that json.loads can read
        result = json.dumps(result)
        logger.debug(result)

        # use decode_word to fill in word fields
        return json.loads(result, object_hook=decode_word)[0]
    else:
        logger.info("{word} not found by DataMuse, or DataMuse service unavailable")


def add_related(word: str, code: str):
    """Query DataMuse for the words related to the Word and add the words to the database.

     The relationship type used is determined by the argument code, which should be one of the strings
     in the list relation_codes"""
    if code not in relation_codes:
        # log error (or raise exception?) and exit
        pass
    else:
        # construct string for function call using word and code and use eval() to run it
        # todo disallow special characters at either end of string word
        # todo determine what (if anything) to return from this function
        code_param = "rel_" + code  # parameter used by python-datamuse

        word_instance = Word.objects.get_or_create(name=word)[0]
        if getattr(word_instance, code).exists():
            # related words for this relation code have already been retrieved from DataMuse
            logger.debug(f'related words for word {word} and code {code} already retrieved, skipping DataMuse query')
            pass

        kwargs = {
            code_param: word,
            "md": "dpf"
        }
        result = query_with_retry(5, 1.0, **kwargs)

        if result:
            # get appropriate field of word_instance to add related words to
            word_attr = getattr(word_instance, code)

            # for each in result, get_or_create Word, update fields from JSON, and add word to appropriate field of word
            for item in result:
                # convert item to string that json.loads can read
                item = json.dumps(item)

                # get or create Word instance and update its fields from JSON
                related_word = json.loads(item, object_hook=decode_word)

                # add this Word to the appropriate field of word_instance
                word_attr.add(related_word)
        else:
            logger.info("DataMuse service unavailable.")


