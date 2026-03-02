from django.db import models

# Create your models here.

class Articles(models.Model):
    title = models.CharField('Article title', max_length=100, null=False, blank=False)
    excerpt = models.CharField('Article excerpt', max_length=250, null=False, blank=False)
    body = models.TextField('Article body', null=False, blank=True)
    published_at = models.DateTimeField('Article published at', null=False, blank=False)

    def get_absolute_url(self):
        return f'/news/{self.id}'

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'