from django import template
from django.template import Context

register = template.Library()

@register.simple_tag
def friend_progress(done, text):
    t = template.loader.get_template("_friend_progress.html")
    return t.render(Context({ "done": done, "text": text }))
