from django.urls import path
from .views import product_list, delete_all_products

urlpatterns = [
    path('', product_list, name='product_list'),
    path('delete-all/', delete_all_products, name='delete_all_products'),
]
