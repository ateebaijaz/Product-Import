
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import Product
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404


def product_list(request):
    products = Product.objects.all().order_by('sku')
    sku = request.GET.get('sku')
    is_active = request.GET.get('is_active')

    if sku:
        products = products.filter(sku__icontains=sku)

    if is_active in ['true', 'false']:
        products = products.filter(is_active=(is_active == 'true'))

    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "products/list.html",
        {
            "products": page_obj,
            "page_obj": page_obj,
            "sku": sku or "",
            "is_active": is_active or "",
        }
    )

@require_POST
def delete_all_products(request):
    Product.objects.all().delete()
    return redirect("/products/")


@require_POST
def toggle_product_active(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    return redirect("/products/")
