from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError

from web.models import Files

User = get_user_model()


def file_size(file):
    limit = 1 * 1024 * 1024
    if file.size > limit:
        raise ValidationError("File too large. size should not exceed 1MB.")


class CustomAuthForm(AuthenticationForm):
    # username = forms.CharField(widget=forms.TextInput(attrs={'class':'validate','placeholder': 'Email'}))
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'})
    )


class SignUpForm(UserCreationForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        max_length=254,
        help_text='',
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )
    # username = None

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('email',)


class FileUploadForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.png, .jpg, .jpeg'}),
        help_text="Allowed file format - .jpg, .jpeg, .png",
        validators=[file_size]
    )

    def save(self, commit=True):
        file = super(FileUploadForm, self).save(commit=False)
        file.file = self.cleaned_data["file"]
        if commit:
            file.save()
        return file

    class Meta:
        model = Files
        fields = ('file',)
