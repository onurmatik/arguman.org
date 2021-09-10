from django.urls import include, path
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page

from blog.sitemaps import BlogSitemap
from nouns.views import ChannelDetail
from profiles.sitemaps import ProfileSitemap
from premises.sitemaps import ArgumentSitemap, PremiseSitemap

admin.autodiscover()

sitemaps = {
    'blog': BlogSitemap(),
    'user': ProfileSitemap(),
    'argument': ArgumentSitemap(),
    'premise': PremiseSitemap()
}

urlpatterns = [
    path('', include('newsfeed.urls')),
    path('', include('premises.urls')),
    path('', include('profiles.urls')),
    path('blog/', include('blog.urls')),
    path('nouns/', include('nouns.urls')),
    path('channels/<slug:slug>', ChannelDetail.as_view(), name="channel_detail"),
    path('', include('social_django.urls')),
    path('admin/', admin.site.urls),
#    path('api/', include('api.urls')),

    # Sitemap
#    path('sitemap\.xml', cache_page(86400)(sitemaps_views.index), {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
#    path('sitemap-(?P<section>.+)\.xml', cache_page(86400)(sitemaps_views.sitemap), {'sitemaps': sitemaps}, name='sitemaps'),
]
