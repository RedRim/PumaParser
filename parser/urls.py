from django.urls import path
from .views import ShoesView, update

urlpatterns = [
    path('', ShoesView.as_view(), name='shoes_list'),
    path('update/', update, name='update'),
]