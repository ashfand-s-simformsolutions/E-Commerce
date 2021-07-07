from .views import *
from django.urls import path

app_name = 'store'

urlpatterns = [
    path('<int:id>/', api_detail_view, name='detail'),
    path('<int:id>/update/', api_update_view, name='update'),
    path('<int:id>/delete/', api_delete_view, name='delete'),
    path('create', api_create_view, name='create '),
    path('list', ApiProductView.as_view(), name='list'),
]