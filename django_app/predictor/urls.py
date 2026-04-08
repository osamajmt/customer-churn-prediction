from django.urls import path
from .views import predict_churn, predict_api

urlpatterns = [
        path("", predict_churn, name="predict"),
        path("api/predict/", predict_api, name="predict_api"),
]