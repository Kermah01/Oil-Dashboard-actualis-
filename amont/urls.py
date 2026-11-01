from django.urls import path
from . import views

urlpatterns = [
    path("", views.page, name="cockpit"),
    path("api/", views.api_index),
    path("api/blocs.geojson", views.api, {"cle": "blocs"}),
    path("api/<slug:cle>.json", views.api),
    path("export/<slug:table>.csv", views.export_csv),
    path("<slug:slug>/", views.page, name="page"),
]
