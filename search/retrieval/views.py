from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from retrieval.models import Article
from retrieval.retrieval_execution.retrieval_execution import RetrievalExecution
from retrieval.paths import *

from datetime import datetime


def index(request):
    string = "Hi page"

    context = {
        'string': string,
    }
    return render(request, 'retrieval/index.html', context)

def results(request):
    form_data = value=request.GET
    
    query = form_data.get('query')

    # validate category and query input, redirect back to home otherwise
    if form_data.get('category') == None:
        return redirect('retrieval:index')
    if query == None:
        return redirect('retrieval:index')

    # validate date in advanced search
    date_start = form_data.get('date_start')
    date_end = form_data.get('date_end')

    # if advanced data search is not switched on, this will not be executed
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

    else:
        retrieval_execution = RetrievalExecution(
            query,
            INDEX_PATH,
            WORD2BYTE_PATH,
            DOC_SIZE_PATH,
            LINKS_PATH,
            9999
        ) # doc_number is hard coded because counting rows in 
          # table is slow. Need to find an alternative for live indexing
        
        ranked_docs = retrieval_execution.execute_ranking('vsm')

        print("talking to database")
        if ranked_docs:    
            # query DB with docnumbers
            results = [Article.objects.get(document_id=doc) for doc in ranked_docs]
        
            context = {
                'results': results,
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