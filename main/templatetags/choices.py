import bisect
import random
from django.template.base import Library, Node, TemplateSyntaxError

register = Library()


def _weighted_random(weights):
    """
    Returns a random index from a list of integers, using the indices'
    respective values to weight the probability of being retured.

    Example:
    _weighted_random([1, 1, 2, 4])
    >>> 0  # 1/8 of the time
    >>> 1  # 1/8 of the time
    >>> 2  # 1/4 of the time
    >>> 3  # 1/2 of the time
    """
    totals = []
    running = 0
    for w in weights:
        running += w
        totals.append(running)
    return bisect.bisect_right(totals, random.random() * totals[-1])


def _get_weight(split_token):
    """
    Parses an argument created by token.split_contents named "weight" to
    determine its integer value. If undefined or empty, returns 1.
    """
    if not split_token:
        return 1
    split_token = split_token.replace("\"", '')
    weight = split_token.replace('weight=', '')
    try:
        return int(weight)
    except ValueError:
        raise TemplateSyntaxError(
            'The value of the weight argument must be an integer'
        )


class ChoiceNode(Node):
    """
    Template node for a block of {% choice %} tags terminating in
    {% endchoice %}
    """
    def __init__(self, choices):
        weights = [choice[0] for choice in choices]
        random_index = _weighted_random(weights)
        self.random = choices[random_index]

    def __repr__(self):
        return "<ChoiceNode>"

    def render(self, context):
        return self.random[1].render(context)


@register.tag
def choice(parser, token):
    """
    Parses a random nodelist of an arbitrary number of weighted choices.

    Example use:

    {% choice %}
        {# Parsed 1/8 of the time #}
    {% choice weight=1 %}
        {# Parsed 1/8 of the time #}
    {% choice weight=2 %}
        {# Parsed 1/4 of the time #}
    {% choice weight=4 %}
        {# Parsed 1/2 of the time #}
    {% endchoice %}
    """

    choices = []

    # One or more {% choice %} nodes
    while token.contents.startswith('choice'):
        split = token.split_contents()
        try:
            tag_name, weight = split
        except ValueError:
            if(len(split) < 2):
                weight = None
            else:
                raise TemplateSyntaxError(
                    '{% choice %} must have a weight argument'
                )

        weight = _get_weight(weight)
        nodelist = parser.parse(('choice', 'endchoice',))
        choices.append((weight, nodelist,))
        token = parser.next_token()

    # {% endchoice %} node
    assert token.contents == 'endchoice'

    return ChoiceNode(choices)
