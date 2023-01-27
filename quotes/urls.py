from django.urls import path, include
from . import views


app_name = 'quotes'
urlpatterns = [
    path('create/', views.create_quote, name='create-quote'),
    path('fetch-quote/', views.fetch_quote, name='fetch-quote'),
    path('submit_quote/', views.submit_quote, name='submit-quote'),
]
