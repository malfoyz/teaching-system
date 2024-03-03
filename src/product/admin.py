from django.contrib import admin

from .models import Group, Lesson, Product, ProductUserAccess


class GroupAdmin(admin.ModelAdmin):
    """Редактор модели группы пользователей"""

    readonly_fields = ('users',)


class ProductUserAccessAdmin(admin.ModelAdmin):
    """Редактор модели доступа пользователей к продуктам."""

    readonly_fields = ('is_waiting_access',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Lesson)
admin.site.register(Product)
admin.site.register(ProductUserAccess, ProductUserAccessAdmin)
