from django.urls import path
from .views import NounDetail, RelationCreate, ChannelDetail

urlpatterns = [
    path('<slug:slug>/', NounDetail.as_view(), name="nouns_detail"),
    path('<slug:slug>/new-relation', RelationCreate.as_view(), name="new_relation"),
]
