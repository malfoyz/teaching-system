from django.http import Http404
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Lesson, Product, ProductUserAccess
from .serializers import LessonSerializer, ProductGetSerializer, \
    ProductPostSerializer, ProductsStatisticSerializer


class LessonViewSet(viewsets.ModelViewSet):
    """Набор представлений для модели урока"""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        product_id = self.request.query_params.get('product_id')

        if not product_id:
            products_access = ProductUserAccess.objects.filter(user=user,
                                                               is_waiting_access=False)
            product_ids = products_access.values_list('product', flat=True)
            return Lesson.objects.filter(product__in=product_ids)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return []

        is_have_access = ProductUserAccess.objects.filter(user=user,
                                                          product=product,
                                                          is_waiting_access=False).exists()
        if not is_have_access:
            return []

        return Lesson.objects.filter(product=product)



class ProductViewSet(viewsets.ModelViewSet):
    """Набор представлений для модели продукта"""

    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductGetSerializer
        return ProductPostSerializer


class ProductsStatisticList(generics.ListAPIView):
    """Представление списка статистик о продуктах"""

    queryset = Product.objects.all()
    serializer_class = ProductsStatisticSerializer
