from django.urls import path
from django.contrib.sitemaps.views import sitemap

from .sitemaps import BlogSitemap
from .views import BlogDetailView, BlogIndexView, \
                        BlogPostsRssFeed, BlogPostsAtomFeed


urlpatterns = [
    # blog urls
    path(r'^$', BlogIndexView.as_view(), name="blog"),
    path(r'^(?P<slug>[-\w]+)/$', BlogDetailView.as_view(), name="blog_detail"),

    # rss & atom feed
    path(r'^feed/rss$', BlogPostsRssFeed(), name="blog_rss_feed"),
    path(r'^feed/atom', BlogPostsAtomFeed(), name="blog_atom_feed"),

    # sitemap
    path('sitemap.xml', sitemap,
        {'sitemaps': {
            "blog": BlogSitemap
        }}, name="blog_sitemap"),
]
