from rest_framework import serializers

from .models import Lesson, Product


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор модели урока"""

    class Meta:
        model = Lesson
        fields = ('name', 'video_url', 'product')


class ProductGetSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра модели продукта"""

    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'start', 'price', 'creator', 'lessons_count')

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class ProductPostSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/изменения модели продукта"""

    class Meta:
        model = Product
        fields = ('id', 'name', 'start', 'price', 'max_group_capacity',
                  'min_group_capacity', 'creator')


class ProductsStatisticSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения статистики по продуктам"""

    lessons_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'start', 'price', 'creator',
                  'lessons_count', 'users_count')

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_users_count(self, obj):
        return sum(group.users.count() for group in obj.groups.all())
