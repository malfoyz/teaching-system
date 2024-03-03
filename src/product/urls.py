from django.urls import include, path
from rest_framework import routers

from .views import LessonViewSet, ProductsStatisticList, ProductViewSet

router = routers.DefaultRouter()
router.register(r'lessons', LessonViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/statistic/', ProductsStatisticList.as_view()),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
]