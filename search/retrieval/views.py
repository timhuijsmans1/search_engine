from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from retrieval.models import TestArticle
from retrieval.retrieval_execution.retrieval_execution import RetrievalExecution
from retrieval.retrieval_helpers.helpers import date_checker

from datetime import datetime

import line_profiler
import atexit

profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)


def index(request):
    string = "Hi page"

    context = {
        'string': string,
    }
    return render(request, 'retrieval/index.html', context)

def results(request):
    start_time = datetime.now()
    first_execution_run = True

    form_data = request.GET

    query = form_data.get('query')
    category = form_data.get('category')
    # validate category and query input, redirect back to home otherwise
    if category == None:
        return redirect('retrieval:index')
    if query == None:
        return redirect('retrieval:index')

    # validate date in advanced search
    date_start = form_data.get('date_start')
    date_end = form_data.get('date_end')

    # init retrieval object
    retrieval_execution = RetrievalExecution(
                        query,
                        first_execution_run
    )

    # if advanced data search is not switched on, dates are None
    if date_start and date_end:

        # check if dates are correct
        valid_bool, start_date_obj, end_date_obj = date_checker(date_start, date_end)
        if valid_bool == False:
            # User will be warned by JS message, so this is just a backend catch
            return redirect('retrieval:index')
        else:
            ranked_article_objects, has_term_been_corrected, corrected_query, original_query = retrieval_execution.execute_ranking(
                           "lm",
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

    retrieval_time = (datetime.now() - start_time).total_seconds()
    # Only return results if relevant documents are found
    if ranked_article_objects:
        # query DB with docnumbers
        results = list(ranked_article_objects.values())
        number_of_results = len(results)

        if date_start and date_end:    
            # change dates to be accepted as url parameters
            date_start = date_start.replace("/", "")
            date_end = date_end.replace("/", "")

        context = {
            'results': results,
            'term_been_corrected': has_term_been_corrected,
            'corrected_query': corrected_query,
            'original_query': original_query,
            'start_of_date_range': date_start,
            'end_of_date_range': date_end,
            'document_category': category,
            'retrieval_time': retrieval_time,
            'number_of_results': number_of_results
        }
        return render(request, 'retrieval/results.html', context)
    else:
        return redirect('retrieval:index')

def rerun_results(request, category, query, date_start, date_end):
    start_time = datetime.now()
    first_execution_run = False

    retrieval_execution = RetrievalExecution(query, first_execution_run)

    # check if the dates have an actual value
    if date_start == "None" and date_end == "None":
        date_start = date_end = None
    # date filter search
    else:
        date_start = datetime.strptime(date_start, '%m%d%Y')
        date_end = datetime.strptime(date_end, '%m%d%Y')
    
    ranked_article_objects, has_term_been_corrected, corrected_query, original_query = retrieval_execution.execute_ranking(
                        "bm25",
                        date_start,
                        date_end,
    )
    
    retrieval_time = (datetime.now() - start_time).total_seconds()
    print(retrieval_time)

    # Only return results if relevant documents are found
    if ranked_article_objects:
        # query DB with docnumbers
        results = list(ranked_article_objects.values())
        number_of_results = len(results)

        context = {
            'results': results,
            'term_been_corrected': False,
            'number_of_results': number_of_results,
            'retrieval_time': retrieval_time
        }
        return render(request, 'retrieval/results.html', context)
    else:
        return redirect('retrieval:index')

def article_detail(request, document_id):
    article = get_object_or_404(TestArticle, pk=document_id)

    context = {
        'article': article,
    }
    return render(request, 'retrieval/detail.html', context)