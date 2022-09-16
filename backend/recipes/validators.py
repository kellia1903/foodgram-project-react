import re

from rest_framework.exceptions import ValidationError

USERNAME_SYMBOLS = re.compile(r'[\w.@+-@./+-]+')

SYMBOLS_ERROR = 'Недопустимые символы: {value}'


class UserValidator:
    def validate_username(self, value):
        if not USERNAME_SYMBOLS.match(value):
            raise ValidationError(
                SYMBOLS_ERROR.format(
                    value=''.join(
                        symbol for symbol in value
                        if not USERNAME_SYMBOLS.match(symbol)
                    )
                )
            )
        return value
