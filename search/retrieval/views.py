from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    string = "Hi page"

    context = {
        'string': string,
    }
    return render(request, 'retrieval/index.html', context)

def results(request):
    form_data = value=request.POST

    # date validator

    context = {
        'category': form_data.get('category'),
        'query': form_data.get('query'),
        'date_start': form_data.get('date_start'),
        'date_end': form_data.get('date_end'),
    }
    return render(request, 'retrieval/results.html', context)