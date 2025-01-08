import hashlib

from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=64, unique=True, verbose_name='Название')
    slug = models.SlugField(
        max_length=64, unique=True, verbose_name='slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=64, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=64, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        db_table = 'ingredient'

    def __str__(self):
        return self.name


class Receipt(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_receipts',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=64, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientReceipt',
        through_fields=('receipt', 'ingredient'),
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagReceipt',
        through_fields=('receipt', 'tag'),
        verbose_name='Ингридиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        null=False,
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(1, 'Минимальное время: 1 минута'),
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    # другие поля
    short_link = models.CharField(
        max_length=20, blank=True, null=True, unique=True)  # Короткая ссылка

    def save(self, *args, **kwargs):
        # Сначала вызываем родительский метод сохранения
        super().save(*args, **kwargs)

        # Если короткая ссылка еще не создана, генерируем и сохраняем
        if not self.short_link:
            self.short_link = self.generate_short_link()
            # Повторное сохранение, чтобы зафиксировать короткую ссылку
            super().save(update_fields=["short_link"])

    def generate_short_link(self):
        # Генерация короткой ссылки на основе уникального идентификатора
        unique_string = f"{self.id}{self.name}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:8]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientReceipt(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_receipt',
        verbose_name='Рецепты'
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Ингредиенты'
    )
    amount = models.IntegerField('Число')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('receipt', 'ingredient'),
                name='unique_ingredient'
            ),
        )
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.receipt} - {self.ingredient}'


class TagReceipt(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='receipts_with_tags',
        verbose_name='Рецепты'
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='tags_of_receipts',
        verbose_name='Теги'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'receipt'),
                name='unique_pair_tags_receipts'
            ),
        )
        verbose_name = 'Теги рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'{self.receipt} - {self.tag}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Покупки',
    )
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='В списке у юзеров'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'receipt'),
                name='unique_receipt'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Юзер {self.user} добавил рецепт {self.receipt} в покупки'


class Favorite(models.Model):
    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name='favorites_of_users',
        verbose_name='Избранное юзеров'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'receipt'),
                name='unique_favorite'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return (
            f'Юзер {self.user} добавил рецепт {self.receipt} в избранное'
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Отслеживаемый автор'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} follows {self.author}'
