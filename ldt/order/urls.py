from django.urls import path
from order import views

app_name = "order"
urlpatterns = [
    path("list", views.OrdersList.as_view(), name="orders_list"),
    path("details/<int:pk>", views.OrderDetails.as_view(), name="orders_details"),
    path("edit/<int:pk>", views.OrderEdit.as_view(), name="orders_edit"),
    path('delete/<int:pk>', views.OrderDeleteView.as_view(), name='order_delete'),
    path("complete/<int:pk>", views.OrderComplete.as_view(), name="orders_complete"),
    path("cancel/<int:pk>", views.OrderСancel.as_view(), name="orders_cancel"),
    path("create", views.OrderCreate.as_view(), name="orders_create"),
    path("export", views.ExportData.as_view(), name="orders_export"),
    path("my", views.OrdersListMy.as_view(), name="orders_my"),
]
