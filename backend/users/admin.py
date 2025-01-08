from django.contrib import admin

from .models import User


class AdminUser(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email')


admin.site.register(User, AdminUser)
