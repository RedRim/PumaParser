from django.urls import path
from .views import ShoesView, update, CardDetailView

urlpatterns = [
    path('', ShoesView.as_view(), name='shoes_list'),
    path('update/', update, name='update'),
    path('card/<slug:card_slug>/', CardDetailView.as_view(), name='card_detail'),
]