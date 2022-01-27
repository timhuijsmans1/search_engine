from django.db import models
from django.urls import reverse

class Article(models.Model):
    document_id = models.IntegerField()
    title = models.CharField(max_length=1000)
    body = models.TextField()
    url = models.URLField()
    publication_date = models.DateField(auto_now=False, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("retrieval:article_detail", kwargs={"document_id": self.document_id})
    