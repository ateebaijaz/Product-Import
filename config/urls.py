
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.shortcuts import redirect


def root_redirect(request):
    return redirect("/products/")

urlpatterns = [
    path("", root_redirect),
    path('admin/', admin.site.urls),
    path('imports/', include('imports.urls')),
    path('products/', include('products.urls')),
]
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
