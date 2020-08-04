from django.contrib import admin
from .models import User_Friend, User_Team, User
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('handle', 'admin')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('handle', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('handle', 'password1', 'password2')}
        ),
    )
    search_fields = ('handle',)
    ordering = ('handle',)
    filter_horizontal = ()

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(User_Friend)
admin.site.register(User_Team)

admin.site.unregister(Group)