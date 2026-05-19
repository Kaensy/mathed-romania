from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Customize Django admin header
admin.site.site_header = "MathEd Romania — Admin"
admin.site.site_title = "MathEd Admin"
admin.site.index_title = "Content Management System"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/content/", include("apps.content.urls")),
    path("api/v1/progress/", include("apps.progress.urls")),
    path("api/v1/pets/", include("apps.pets.urls")),
]

# Debug toolbar + dev media serving (dev only). Production media storage
# is out of scope; deferred until a production host is chosen.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
