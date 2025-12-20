from django.urls import path

from imports import views
from .views import product_list, delete_all_products, toggle_product_active, product_create, product_edit, product_delete

urlpatterns = [
    path('', product_list, name='product_list'),
    path('delete-all/', delete_all_products, name='delete_all_products'),
    path('toggle/<int:product_id>/', toggle_product_active, name='toggle_product_active'),
    path("create/", product_create, name="product_create"),
    path("<int:pk>/edit/", product_edit, name="product_edit"),
    path("<int:pk>/delete/", product_delete, name="product_delete"),

]
