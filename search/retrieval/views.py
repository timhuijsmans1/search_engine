from django.shortcuts import render, redirect
from django.http import HttpResponse

from datetime import datetime


def index(request):
    string = "Hi page"

    context = {
        'string': string,
    }
    return render(request, 'retrieval/index.html', context)

def results(request):
    form_data = value=request.GET

    # validate form input, redirect back to home otherwise
    if form_data.get('category') == None:
        return redirect('retrieval:index')
    if form_data.get('query') == None:
        return redirect('retrieval:index')

    # validate date in advanced search
    date_start = form_data.get('date_start')
    date_end = form_data.get('date_end')

    if date_start and date_end:
        now = datetime.now()

        # check if dates are in expected format and valid
        try:
            date_start_obj = datetime.strptime(date_start, '%m/%d/%Y')
            date_end_obj = datetime.strptime(date_end, '%m/%d/%Y')
        except:
            return redirect('retrieval:index')

        # check if start is before end date
        if date_end_obj < date_start_obj:
            return redirect('retrieval:index')

        # check if date interval starts in the past or today
        if date_start_obj > now:
            return redirect('retireval:index')
        
        # TODO
        # advanced query: retrieve doc numbers, query database for doc numbers and date

        context = {
            'category': form_data.get('category'),
            'query': form_data.get('query'),
            'date_start': form_data.get('date_start'),
            'date_end': form_data.get('date_end'),
        }

    # TODO
    # standard: retrieve doc numbers, query database for doc numbers only
    
    else:
        context = {
            'category': form_data.get('category'),
            'query': form_data.get('query'),
        }
    return render(request, 'retrieval/results.html', context)