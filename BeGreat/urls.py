from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("api.urls")),
    path('auth/', include("autho.urls")),
    path('courses/', include("course.urls")),
    path('support/', include("support.urls")),
    path('achievement/', include("achievement.urls"))
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar
    from drf_spectacular.views import SpectacularAPIView, \
        SpectacularSwaggerView, SpectacularRedocView
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]