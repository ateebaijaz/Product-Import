
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import Product
from django.views.decorators.http import require_POST


def product_list(request):
    products = Product.objects.all().order_by('sku')
    paginator = Paginator(products, 50)  # 50 per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "products/list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
        }
    )

@require_POST
def delete_all_products(request):
    Product.objects.all().delete()
    return redirect("/products/")
