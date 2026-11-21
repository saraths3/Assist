from django.urls import path
from .views import info, file_process

urlpatterns = [
    path('info/', info, name='info'),
    path('file/', file_process, name= 'file_process')
]