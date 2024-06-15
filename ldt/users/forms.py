from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, )
from django.utils import timezone
from users.models import User


class CustomLoginChangeForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "birthday",
            "password1",
            "password2",
            "avatar"
        )

        widgets = {
            "birthday": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.visible_fields():
            field.field.widget.attrs["id"] = field.name
            field.field.widget.attrs["name"] = field.name
            field.field.widget.attrs["class"] = "form-control"

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")

        if birthday and birthday > timezone.now().date():
            raise forms.ValidationError("День рождения не может быть в будущим")

        return birthday


class UserToChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "birthday",
            "avatar"
        )

        widgets = {
            "birthday": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")

        if birthday and birthday > timezone.now().date():
            raise forms.ValidationError("Birthday cannot be in the future.")

        return birthday
