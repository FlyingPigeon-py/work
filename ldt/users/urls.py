import django.contrib.auth.views
import users.views
from django.urls import path
from users import views

app_name = "user"
urlpatterns = [
    path(
        "login/",
        django.contrib.auth.views.LoginView.as_view(
            template_name="users/login.html",
            next_page="user:profile",
            form_class=users.forms.CustomLoginChangeForm,
        ),
        name="login",
    ),

    path("register", views.UserRegistrationView.as_view(), name="register"),
    path("logout/",
         django.contrib.auth.views.LogoutView.as_view(next_page="user:login"),
         name="logout",
         ),
    path("profile", views.ProfileEditView.as_view(), name="profile"),
    path("userslist", views.UsersListView.as_view(), name="userslist"),
    path("search/<str:search>", views.UsersSearchView.as_view(), name="search"),
    path("userdetail/<int:pk>/", views.UserDetailView.as_view(), name="userdetail"),
]
