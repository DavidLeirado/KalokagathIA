from django.http import HttpResponse
from django.template.loader import get_template

def home(request):
    return HttpResponse(get_template('frontpage.html').render())
