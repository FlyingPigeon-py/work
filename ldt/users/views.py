from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView
from order.models import Order
from users.forms import SignUpForm, UserToChangeForm
from users.models import User


class UserRegistrationView(CreateView):
    form_class = SignUpForm
    template_name = "users/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def get_success_url(self):
        return reverse_lazy("user:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.capitalize()}: {error}')
        return super().form_invalid(form)


class ProfileEditView(LoginRequiredMixin, FormView):
    template_name = "users/profile.html"
    form_class = UserToChangeForm
    success_url = reverse_lazy("users:profile")
    login_url = reverse_lazy("users:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(instance=self.request.user)
        context["time"] = self.request.user.last_login

        if self.request.user.is_staff:
            context["order_count"] = Order.objects.all().count()
            context["order_not_assigned_count"] = Order.objects.filter(employee=None, status=False).count()
            context["order_done_count"] = Order.objects.filter(status=True).count()
            context["order_in_progress_count"] = context["order_count"] - context["order_done_count"] - context[
                "order_not_assigned_count"]
        else:
            context["order_count"] = Order.objects.get_orders_count_for_employee(self.request.user)
            context["order_done_count"] = Order.objects.get_orders_done_count_for_employee(self.request.user)
            context["order_in_progress_count"] = context["order_count"] - context["order_done_count"]
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            self.request.POST,
            self.request.FILES,
            instance=self.request.user,
        )
        if form.is_valid():
            form.save()
            return redirect("user:profile")
        return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.capitalize()}: {error}')
        return super().form_invalid(form)


class UsersSearchView(UserPassesTestMixin, View):
    template_name = "users/userlist.html"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get(self, request, search):
        users = User.objects.filter(Q(email__icontains=search) | Q(
            first_name__icontains=search.lower().capitalize()) | Q(last_name__icontains=search.lower().capitalize()))
        context = {"user_list": users, "search": search}
        return render(request, self.template_name, context)


class UsersListView(UserPassesTestMixin, View):
    template_name = "users/userlist.html"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        context = {"user_list": users, "search": ""}
        return render(request, self.template_name, context)


class UserDetailView(UserPassesTestMixin, View):
    template_name = "users/userdetail.html"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff or (
                    self.request.user.id == self.kwargs.get('pk'))

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        context = {"userl": user}
        return render(request, self.template_name, context)
