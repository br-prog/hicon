from django.urls import path
from .views import *


urlpatterns = [
    path('', homework, name='homework'),
    path('pomodoro/', pomodoro, name='pomodoro'),
    path('matrix/', matrix, name='matrix'),
    path('notes/', notes, name='notes')
]