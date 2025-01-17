from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from markitup.fields import MarkupField


class PublishedManager(models.Manager):
    """
    Returns published blog posts.
    """
    def get_queryset(self):
        queryset = super(PublishedManager, self).get_queryset()
        return queryset.filter(is_published=True)


class Post(models.Model):
    """
    Holds blog post data.
    """
    title = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)
    content = MarkupField(_("Content"))
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(_("Published"), default=True)
    is_announcement = models.BooleanField(default=False)

    objects = models.Manager()
    published_objects = PublishedManager()

    class Meta:
        ordering = ("-date_created", )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])
