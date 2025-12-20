from django.urls import path
from .views import product_list, delete_all_products, toggle_product_active

urlpatterns = [
    path('', product_list, name='product_list'),
    path('delete-all/', delete_all_products, name='delete_all_products'),
    path('toggle/<int:product_id>/', toggle_product_active, name='toggle_product_active'),

]
