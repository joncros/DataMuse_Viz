import time

from django.core.exceptions import ValidationError

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
            logger.info('DataMuse query failed.')
            time.sleep(wait)
    # no response after retries exhausted
    raise ConnectionError('DataMuse service unavailable')


def decode_word(dct):
    """Decodes a json response corresponding to a single word to get a Word object"""
    if not dct:
        raise ValueError("Invalid parameter: empty json")
    else:
        word = Word.objects.get_or_create(name=dct['word'])[0]

        # update word to indicate successful DataMuse query
        word.datamuse_success = True

        # process dct['tags'], which is a dictionary that can contain frequency and part(s) of speech
        tags = dct['tags']
        for tag in tags:
            if tag in possible_parts_of_speech:
                part = PartOfSpeech.objects.get_or_create(name=tag)[0]
                word.parts_of_speech.add(part)
            elif tag[:2] == 'f:':
                word.frequency = float(tag[2:])

        # add definitions if present
        if 'defs' in dct:
            word.definitions = dct['defs']

        word.save()
        return word


def add_or_update_word(word: str):
    """Query DataMuse for the parts_of_speech, frequency and definitions of a Word

    Returns the corresponding Word instance, or None if the query was unsuccessful"""
    if not word or word.isspace():
        # exit early if word is empty or only whitespace
        return None

    word = word.lower()

    if Word.objects.filter(name=word).exists() and Word.objects.get(name=word).datamuse_success is True:
        # word already in database and Datamuse call already successfully performed. Skip DataMuse query
        logger.debug(f'{word} values already populated from DataMuse')
        return Word.objects.get(name=word)

    # do api query, give up after 5 attempts
    try:
        result = query_with_retry(5, 1.0, sp=word, md='dpf', max=1)
    except ConnectionError as e:
        logger.error(e)
        return None

    # check if result is not empty and the entry is a word that exactly matches the parameter
    if result and result[0]['word'] == word:
        # convert result to string that json.loads can read
        # result is a list (of size one because api parameter max=1) of json objects holding data concerning the word
        result = json.dumps(result[0])
        logger.debug(f'json from Datamuse: {result}')

        # use decode_word to fill in word fields, return the Word object
        return json.loads(result, object_hook=decode_word)
    else:
        logger.info(f'json from Datamuse: {result}')
        logger.info(f'{word} not found by DataMuse')


def add_related(word: str, code: str):
    """Query DataMuse for the words related to the Word and add the words to the database.

     The relationship type used is determined by the argument code, which should be one of the strings
     in the list relation_codes. Returns the Word corresponding to word and the QuerySet of related words."""
    if code not in relation_codes:
        raise ValueError(f'{code} is not a valid related word code.')
    else:
        # construct string for function call using word and code and use eval() to run it
        word = word.lower()
        code_param = "rel_" + code  # parameter used by python-datamuse

        word_instance = Word.objects.get_or_create(name=word)[0]

        # the related word field for the word
        word_attr = getattr(word_instance, code)

        # the corresponding set of relationships (relationship being a subclass of models.WordRelation)
        relations = getattr(word_instance, f'{code}_relations')

        if word_attr.exists():
            logger.debug(f'related words for word {word} and code {code} already retrieved, skipping DataMuse query')
            return word_instance, relations

        kwargs = {
            code_param: word,
            "md": "dpf"
        }
        result = query_with_retry(5, 1.0, **kwargs)

        if result:
            for item in result:
                # get the word's score value (it's relevance compared to other words in the query)
                score = item['score']

                # convert item to string that json.loads can read
                item = json.dumps(item)

                # get or create Word instance and update its fields from JSON
                related_word = json.loads(item, object_hook=decode_word)
                logger.debug(f'word: {word}, code: {code}, related word: {related_word.name}, score: {score}')

                # add this Word to the appropriate field of word_instance
                word_attr.add(related_word, through_defaults={'score': score})

            return word_instance, relations
        else:
            verbose_code = Word._meta.get_field(code).verbose_name
            raise ValidationError(f"'{word}' not found by DataMuse, or no related words found for {verbose_code}")
