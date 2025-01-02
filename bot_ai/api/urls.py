from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from . import views

router = DefaultRouter() if settings.DEBUG else SimpleRouter()


urlpatterns = [
    path("ai-data/company-data/", views.CompanyDataView.as_view(), name="company-data"),
    path(
        "ai-data/product-data/",
        views.ProductDataListView.as_view(),
        name="product-data-list",
    ),
]
