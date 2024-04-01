"""
URL configuration for cash_flow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path


from django.contrib import admin
from django.urls import path, include
from common.router import OptionalSlashRouter
from common.router import OptionalSlashRouter
from django.conf import settings

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from depenses.views import ExpenseSheetViewSet
from articlemanagement.views import FamilyArticleViewSet, ArticleViewSet


router = OptionalSlashRouter()

router.register(r'expensesheet', ExpenseSheetViewSet, basename='expensesheet')
router.register(r'familyarticle', FamilyArticleViewSet, basename='familyarticle')
router.register(r'article', ArticleViewSet, basename='article')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # Ajoutez le chemin pour l'action rejection
    # path('expensesheet/<str:pk>/rejection/', ExpenseSheetViewSet.as_view({'patch': 'rejection'}), name='expensesheet-rejection'),
]

# ajoutéer l'url de débug
if settings.DEBUG:
    # from django.urls import include, path

    urlpatterns = [
        # ...
        path('__debug__/', include('debug_toolbar.urls')),
    ]+urlpatterns
