from translate import Translator
from Schedule import get_motivational_quote

translator = Translator(to_lang='ru')


def motivate_students():
    quote = get_motivational_quote()
    return translator.translate(quote['quote'])
