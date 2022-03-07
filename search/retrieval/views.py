from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from retrieval.models import Article
from retrieval.retrieval_execution.retrieval_execution import RetrievalExecution
from retrieval.retrieval_helpers.helpers import date_checker

from datetime import datetime


def index(request):
    string = "Hi page"

    context = {
        'string': string,
    }
    return render(request, 'retrieval/index.html', context)

def results(request):
    form_data = value = request.GET

    query = form_data.get('query')

    # validate category and query input, redirect back to home otherwise
    if form_data.get('category') == None:
        return redirect('retrieval:index')
    if query == None:
        return redirect('retrieval:index')

    # validate date in advanced search
    date_start = form_data.get('date_start')
    date_end = form_data.get('date_end')

    # init retrieval object
    retrieval_execution = RetrievalExecution(
                        query,
                        1000 # change the hardcoded document number accordingly
    )

    # if advanced data search is not switched on, dates are None
    if date_start and date_end:

        # check if dates are correct
        valid_bool, start_date_obj, end_date_obj = date_checker(date_start, date_end)
        if valid_bool == False:
            return redirect('retrieval:index')
        else:
            ranked_article_objects, has_term_been_corrected, query = retrieval_execution.execute_ranking(
                           'lm',
                           start_date_obj,
                           end_date_obj
            )

    # this is executed only if date_start and date_end are None
    else:
        ranked_article_objects, has_term_been_corrected, corrected_query, original_query = retrieval_execution.execute_ranking(
                           'lm',
                           date_start,
                           date_end
        )

    # Only return results if relevant documents are found
    if ranked_article_objects:
        # query DB with docnumbers
        results = list(ranked_article_objects.values())

        context = {
            'results': results,
            'term_been_corrected': has_term_been_corrected,
            'corrected_query': corrected_query,
            'original_query': original_query
        }
        return render(request, 'retrieval/results.html', context)
    else:
        return redirect('retrieval:index')

def article_detail(request, document_id):
    article = get_object_or_404(Article, document_id=document_id)

    context = {
        'article': article,
    }
    return render(request, 'retrieval/detail.html', context)