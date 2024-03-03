from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Модель продукта"""

    name = models.CharField(
        _('Название'),
        max_length=150,
    )
    start = models.DateTimeField(
        _('Дата и время старта'),
        default=timezone.now,
    )
    price = models.DecimalField(
        _('Стоимость'),
        max_digits=8,
        decimal_places=2,
        default=0.00,
    )
    max_group_capacity = models.PositiveIntegerField(
        _('Максимальное число учащихся'),
        default=4,
    )
    min_group_capacity = models.PositiveSmallIntegerField(
        _('Минимальное число учащихся'),
        default=3,
    )
    creator = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='own_products',
        related_query_name='own_product',
        verbose_name=_('Создатель'),
    )

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')

    def __str__(self):
        return self.name


class ProductUserAccess(models.Model):
    """Модель доступа пользователя к продукту"""

    is_waiting_access = models.BooleanField(
        _('Ожидает доступ'),
        default=False,
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='access_users',
        related_query_name='access_user',
        verbose_name=_('Продукт'),
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='access_products',
        related_query_name='access_product',
        verbose_name=_('Пользователь'),
    )

    class Meta:
        verbose_name = _('Доступ пользователя к продукту')
        verbose_name_plural = _('Доступы пользователей к продуктам')

    def __str__(self):
        return f"{self.product.name}: {self.user.username}"

    def save(self, *args, **kwargs):
        min_capacity = self.product.min_group_capacity
        max_capacity = self.product.max_group_capacity

        users_is_waiting = [user for user in ProductUserAccess.objects.filter(
            product=self.product, is_waiting_access=True)]
        groups = [group for group in Group.objects.filter(product=self.product)]

        # 1. Считаем общее число студентов
        total_users_count = len(users_is_waiting)
        if groups:
            total_users_count += ProductUserAccess.objects.filter(
                product=self.product, is_waiting_access=False).count()

        groups_count = len(groups)
        group_size_avg = total_users_count / groups_count if groups_count else 0
        group_size_avg_next = (total_users_count + 1) / (groups_count + 1)

        # 2.1. Если студентов в продукте меньше, чем минимально возможное число студентов в группе,
        #      то студент должен ожидать, пока не наберется необходимое число людей.
        if total_users_count < min_capacity:
            self.is_waiting_access = True
            users_is_waiting.append(self)

            # 2.1.1. Если же при вступлении студента в продукт, людей стало достаточно для набора группы,
            #        тогда создаем эту группу.
            if len(users_is_waiting) >= min_capacity:
                for user in users_is_waiting:
                    user.is_waiting_access = False

                primary_keys = [user.pk for user in users_is_waiting]
                if primary_keys:
                    ProductUserAccess.objects.filter(pk__in=primary_keys)\
                        .update(is_waiting_access=False)

                new_group = Group(name='Группа', product=self.product)
                new_group.save()
                new_group.users.set([access.user for access in users_is_waiting])
                groups.append(new_group)
                users_is_waiting.clear()
        # 2.2.
        elif group_size_avg_next <= min_capacity:
            if group_size_avg < max_capacity:
                groups = sorted(groups, key=lambda g: len(g.users.all()), reverse=True)
                groups[-1].users.add(self.user)
            else:
                self.is_waiting_access = True
                users_is_waiting.append(self)
                if group_size_avg_next == min_capacity:
                    for user in users_is_waiting:
                        user.is_waiting_access = False
                    new_group = Group(name='Группа', product=self.product)
                    new_group.save()
                    new_group.users.set([access.user for access in users_is_waiting])
                    groups.append(new_group)
                    users_is_waiting.clear()
                    groups_count += 1

                    for g in range(groups_count):
                        while groups[g].users.count() > group_size_avg_next:
                            user = groups[g].users.last()
                            groups[-1].users.add(user)
                            groups[g].users.remove(user)

        # 2.3. Если студентов в продукте достаточно хотя бы для одной группы, то добавляем текущего студента
        #      в одну из групп и сортируем группы при необходимости.
        else:
            # 2.3.1. Если группы не заполнены полностью, то добавляем студента в самую маленькую группу.
            if group_size_avg < max_capacity:
                group = sorted(groups, key=lambda g: len(g.users.all()))[0]
                if group.users.count() <= int(group_size_avg):
                    group.users.add(self.user)

            # 2.3.2. Если группы полностью заполнены, то создаем новую группу, добавляем туда студента,
            #        и сортируем все группы так, чтобы ни в одной из них число студентов не отличалось более, чем на 1.
            else:
                new_group = Group(name='Группа', product=self.product)
                new_group.save()
                new_group.users.set([self.user])
                groups.append(new_group)

                groups_count += 1
                total_users_count += 1
                group_size_avg = total_users_count // groups_count

                # число групп, в которых студентов будет больше среднего на 1
                remaining_students_count = total_users_count % groups_count - 1

                for g in range(groups_count - 1):
                    if remaining_students_count > 0:
                        while groups[g].users.count() > group_size_avg + 1:
                            user = groups[g].users.last()
                            groups[-1].users.add(user)
                            groups[g].users.remove(user)
                            remaining_students_count += 1
                    else:
                        while groups[g].users.count() > group_size_avg:
                            user = groups[g].users.last()
                            groups[-1].users.add(user)
                            groups[g].users.remove(user)

                if groups[-1].users.count() < group_size_avg:
                    k = group_size_avg - groups[-1].users.count()
                    groups = sorted(groups, key=lambda g: len(g.users.all()), reverse=True)
                    for g in range(groups_count):
                        if groups[g].users.count() > group_size_avg:
                            user = groups[g].users.last()
                            groups[-1].users.add(user)
                            groups[g].users.remove(user)
                            k -= 1
                            if k <= 0:
                                break

        [group.save() for group in groups]
        super().save(*args, **kwargs)    # сохраняем запись



class Lesson(models.Model):
    """Модель урока"""

    name = models.CharField(
        _('Название'),
        max_length=150,
    )
    video_url = models.CharField(
        _('Ссылка на видео'),
        max_length=2100,
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='lessons',
        related_query_name='lesson',
        verbose_name=_('Продукт'),
    )

    class Meta:
        verbose_name = _('Урок')
        verbose_name_plural = _('Уроки')

    def __str__(self):
        return f"{self.product.name}: {self.name}"


class Group(models.Model):
    """Модель группы пользователей"""

    name = models.CharField(
        _('Название'),
        max_length=150,
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='groups',
        related_query_name='group',
        verbose_name=_('Группа'),
    )
    users = models.ManyToManyField(
        to=User,
        related_name='user_groups',
        related_query_name='user_group',
    )

    class Meta:
        verbose_name = _('Группа')
        verbose_name_plural = _('Группы')

    def __str__(self):
        return self.name