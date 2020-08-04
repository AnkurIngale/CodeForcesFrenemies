from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .api import verifyHandle
from .models import User

class UserAdminCreationForm(forms.ModelForm):
    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('handle','email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_handle(self):
        # Check if handle exists
        c_handle = self.cleaned_data['handle']
        try:
            user = User.objects.get(handle = c_handle)
        except User.DoesNotExist:
            if not verifyHandle(c_handle):
                raise forms.ValidationError("Handle does not exist")
        else:
            raise forms.ValidationError("Handle already registered")
        return c_handle

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('handle','email', 'password', 'active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class LoginForm(forms.Form):
    handle = forms.CharField(label = 'Handle' , widget=forms.TextInput)
    password = forms.CharField(label = 'Password' , widget=forms.PasswordInput)
    
    def clean_handle(self):
        c_handle = self.cleaned_data['handle']
        try:
            user = User.objects.get(handle = c_handle)
        except User.DoesNotExist:
            raise forms.ValidationError('Handle not registered')
        return c_handle

class AddFriendForm(forms.Form):
    handle = forms.CharField(label = 'Friend Handle' , widget=forms.TextInput)

    def clean_handle(self):
        c_handle = self.cleaned_data['handle']
        try:
            user = User.objects.get(handle = c_handle)
        except User.DoesNotExist:
            if not verifyHandle(c_handle):
                raise forms.ValidationError('Handle does not exist')
        return c_handle
