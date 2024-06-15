import django.contrib.auth.models
import django.template.loader
from django.contrib.auth.backends import ModelBackend
from users.models import User

usermodel = django.contrib.auth.get_user_model()


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(usermodel.USERNAME_FIELD)
        if username is None or password is None:
            return None
        try:
            if "@" in username:
                user = User.objects.by_mail(
                    email=username,
                )
            else:
                user = usermodel._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            usermodel().set_password(password)
        else:
            if user:
                if user.check_password(password):
                    user.save()
                    return user

    def get_user(self, user_id):
        try:
            user = usermodel._default_manager.get(pk=user_id)
        except usermodel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


__all__ = []
