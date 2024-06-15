import os
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from order.forms import CreateOrderForm
from order.models import Order
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from users.models import User
from order.forms import EditOrderForm


class OrdersList(UserPassesTestMixin, View):
    template_name = "order/orders_list.html"

    def get(self, request):
        not_assigned = Order.objects.orders_without_employee
        assigned = Order.objects.orders_with_employee_false_status
        done = Order.objects.orders_with_status_true

        context = {
            "not_assigned": not_assigned,
            "assigned": assigned,
            "done": done,
        }
        return render(request, self.template_name, context)

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class OrdersListMy(LoginRequiredMixin, View):
    template_name = "order/orders_list_my.html"
    login_url = reverse_lazy("users:login")

    def get(self, request):
        assigned = Order.objects.orders_with_employee_false_status_for_employee(self.request.user)
        done = Order.objects.orders_with_status_true_for_employee(self.request.user)

        context = {
            "assigned": assigned,
            "done": done,
        }
        return render(request, self.template_name, context)


class OrderDetails(LoginRequiredMixin, View):
    template_name = "order/order_details.html"

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        context = {
            "order": order,
        }
        return render(request, self.template_name, context)


class OrderCreate(UserPassesTestMixin, FormView):
    form_class = CreateOrderForm
    template_name = "order/order_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(
            self.request.POST or None,
            files=self.request.FILES,
        )

        return context

    def form_valid(self, form):
        data = self.request.POST

        delivery_date = data["delivery_date"] if data["delivery_date"] else None

        order = Order.objects.create(
            status=False,
            name=data["name"],
            address=data["address"],
            client=data["client"],
            contact_number=data["contact_number"],
            payment_method=data["payment_method"],
            price=data["price"],
            description=data["description"],
            delivery_date=delivery_date
        )
        order.save()

        self.success_url = reverse(
            "order:orders_list",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.capitalize() + ":" if field != "__all__" else ""} {error}')
        return super().form_invalid(form)

    def test_func(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False


class OrderEdit(UserPassesTestMixin, UpdateView):
    model = Order
    form_class = EditOrderForm
    template_name = "order/order_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = Order.objects.get(pk=self.kwargs["pk"])
        context["order"] = order
        context["form"] = self.form_class(instance=order)
        return context

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        form = self.form_class(
            self.request.POST or None,
            self.request.FILES,
            instance=order,
        )
        form.save()
        self.success_url = reverse(
            "order:orders_list",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.capitalize() + ":" if field != "__all__" else ""} {error}')
        return super().form_invalid(form)

    def test_func(self):
        order = Order.objects.get(pk=self.kwargs["pk"])
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return order.employee == self.request.user


class OrderComplete(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        order.status = True
        order.save()

        if self.request.user.is_staff:
            return redirect(reverse(
                "order:orders_list",
            ))
        else:
            return redirect(reverse(
                "order:orders_my",
            ))


class OrderСancel(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        order.status = False
        order.save()

        if self.request.user.is_staff:
            return redirect(reverse(
                "order:orders_list",
            ))
        else:
            return redirect(reverse(
                "order:orders_my",
            ))


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "order/orders_list.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(reverse(
            "order:orders_list",
        ))

    def get_success_url(self):
        return redirect(reverse(
            "order:orders_list",
        ))


class ExportData(TemplateView):
    template_name = "order/export_data.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data_range = request.POST.get("range")

        if data_range == "mounth":
            orders = Order.objects.orders_created_this_month()
        else:
            orders = Order.objects.orders_created_today()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Report  ({" - ".join(get_month_boundaries()) if data_range == "month" else datetime.now().strftime("%d.%m.%y")}).pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        pdfmetrics.registerFont(TTFont('Roboto-Black', 'order/fonts/Roboto-Black.ttf'))
        title_style = ParagraphStyle(
            "Title",
            fontName="Roboto-Black",
            fontSize=18,
            textColor=colors.black,
            alignment=1,
            spaceAfter=12
        )
        title = Paragraph("Отчет", title_style)

        subtitle_style = ParagraphStyle(
            "Subtitle",
            fontName="Roboto-Black",
            fontSize=14,
            textColor=colors.black,
            alignment=1,
            spaceAfter=12
        )

        if data_range == "day":
            subtitle = Paragraph(f"Отчет по заказам за {datetime.now().strftime('%d.%m.%y')}", subtitle_style)
        else:
            subtitle = Paragraph(f"Отчет по заказам с {' по '.join(get_month_boundaries())}", subtitle_style)

        elements.append(title)
        elements.append(subtitle)

        data = [
            ['№', 'Название', "Исполнитель", 'Дата', 'Время', "Цена"],
        ]

        for order in orders:
            data.append((order.id, order.name, order.employee, order.creation_time.strftime("%d-%m-%Y"),
                         order.creation_time.strftime("%H:%M"), order.price))

        table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto-Black'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Black'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        table = Table(data)
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)

        return response


def get_month_boundaries():
    current_date = datetime.now()
    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timedelta(days=1)
    first_day_formatted = first_day_of_month.strftime("%d-%m-%Y")
    last_day_formatted = last_day_of_month.strftime("%d-%m-%Y")
    return first_day_formatted, last_day_formatted
