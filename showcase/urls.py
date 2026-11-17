from django.contrib import admin
from django.urls import path
from showcase.views import index  # Update to match your view function name if different

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index, name="index"),
]