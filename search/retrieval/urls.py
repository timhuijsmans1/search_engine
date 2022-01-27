from django.urls import path

from . import views

app_name = "retrieval"

urlpatterns = [
    path('', views.index, name='index'),
    path('results', views.results, name='results'),
    path('article/<int:document_id>', views.article_detail, name="article_detail")
]