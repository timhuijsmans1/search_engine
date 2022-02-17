from django.db import models
from django.urls import reverse

class Article(models.Model):
    document_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    url = models.URLField(max_length=1000)
    publication_date = models.DateField(auto_now=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("retrieval:article_detail", kwargs={"document_id": self.document_id})

class TestArticle(models.Model):
    document_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    url = models.URLField(max_length=1000)
    content = models.TextField()
    publication_date = models.DateField(auto_now=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("retrieval:article_detail", kwargs={"document_id": self.document_id})

class MlArticle(models.Model):
    document_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    url = models.URLField(max_length=1000)
    content = models.TextField()
    publication_date = models.DateField(auto_now=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("retrieval:article_detail", kwargs={"document_id": self.document_id})
    
