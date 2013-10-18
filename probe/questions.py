#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from recurrent import RecurringEvent

from .errors import AnswerError

class Question(object):
    def __init__(self, config):
        self.key, self.config = config.items()[0]

        parser = RecurringEvent(now_date=datetime.now())

        # set attributes
        self.unit = self.config.get('unit', 'number')
        self.interval = parser.parse(self.config['interval'])
        self.text = self.config['text']

    def hint(self):
        hint = 'default: %r' % self.default
        if self.lower and self.upper:
            hint += ', range: %r to %r' % (self.lower, self.upper)
        elif self.lower:
            hint += ', lower: %r' % self.lower
        elif self.upper:
            hint += ', upper: %r' % self.upper

        return hint

    def __repr__(self):
        return '<%s: key: %s, %s>' % (
            self.__class__.__name__, 
            self.key,
            self.hint()
        )


class NumberQuestion(Question):
    def __init__(self, config):
        super(NumberQuestion, self).__init__(config)
        self.converter = float
        self._type = 'number'

        self.lower = self.config.get('lower', None)
        self.upper = self.config.get('upper', None)
        self.default = self.config.get('default', 0)

    def parse_answer(self, ans):
        try:
            ans = self.converter(ans)
        except ValueError:
            raise AnswerError('Could not parse "%r" as a %s' % (ans, self._type))

        if self.lower and ans < self.lower:
            raise AnswerError(
                '"%r" was lower than the lower bound, %r' % (ans, self.lower)
            )

        if self.upper and ans > self.upper:
            raise AnswerError(
                '"%r" was higher than the upper bound, %r' % (ans, self.upper)
            )

        return ans


class HoursQuestion(NumberQuestion):
    def __init__(self, config):
        super(HoursQuestion, self).__init__(config)

        self.lower = self.config.get('lower', 0)
        self.default = self.config.get('default', 8)


class RatingQuestion(NumberQuestion):
    def __init__(self, config):
        super(RatingQuestion, self).__init__(config)

        self.converter = int
        self._type = 'integer'

        self.lower = self.config.get('lower', 0)
        self.upper = self.config.get('upper', 10)


class YesNoQuestion(Question):
    def __init__(self, config):
        super(YesNoQuestion, self).__init__(config)

        self.upper = None
        self.lower = None
        self.default = False

    def parse_answer(self, ans):
        if ans.lower().startswith('y'):
            return True
        elif ans.lower().startswith('f'):
            return False

        try:
            ans_i = int(ans)
            if ans_i == 1:
                return True
            elif ans_i == 0:
                return False
        except ValueError:
            pass

        raise AnswerError('Can\'t handle "%s" as Yes/No' % ans)
