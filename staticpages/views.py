from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request, page_name):
    return render_to_response(
        "static_{0}.html".format(page_name),
        context_instance=RequestContext(request))
