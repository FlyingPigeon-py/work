from django import forms

from order.models import Order

from users.models import User


class EditOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "name",
            "price",
            "employee",
            "description",
            "contact_number",
            "client",
            "address",
            "payment_method",
            "delivery_date"
        )

    widgets = {
        'delivery_date': forms.TextInput(attrs={'type': 'datetime-local'}),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["id"] = field.name
            field.field.widget.attrs["name"] = field.name
            field.field.widget.attrs["class"] = "form-control"

        self.fields['employee'].queryset = User.objects.filter(is_staff=False)


class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "name",
            "price",
            "description",
            "contact_number",
            "client",
            "address",
            "payment_method",
            "delivery_date"
        )

    widgets = {
        'delivery_date': forms.TextInput(attrs={'type': 'datetime-local'}),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["id"] = field.name
            field.field.widget.attrs["name"] = field.name
            field.field.widget.attrs["class"] = "form-control"
