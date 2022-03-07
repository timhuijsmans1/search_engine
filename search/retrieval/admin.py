from django.contrib import admin

from .models import Article
from .models import TestArticle

admin.site.register(Article)
admin.site.register(TestArticle)
