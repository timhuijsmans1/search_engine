from django.db import models

class Article(models.Model):
    document_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    body = models.TextField()
    url = models.URLField()
    publication_date = models.DateField(auto_now=False, null=True, blank=True)