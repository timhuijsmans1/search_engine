from django.urls import path

from . import views

app_name = "retrieval"

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('rerun_query/<str:query>/<str:date_start>/<str:date_end>', views.rerun_results, name='rerun_results'),
    path('article/<int:document_id>', views.article_detail, name="article_detail")
]