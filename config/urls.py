from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login page
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='inventory_app/login.html'),
        name='login'
    ),

    # Logout page (redirects to login after logout)
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # Inventory App URLs (dashboard, products, categories, stock, profile, etc.)
    path('', include('inventory_app.urls')),

    # Sales App URLs
    path('sales/', include('sales.urls', namespace='sales')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
