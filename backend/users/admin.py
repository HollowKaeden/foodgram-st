from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Subscription


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    model = MyUser
    search_fields = ('email', 'username')


admin.site.register(Subscription)
