from django.urls import path
from Agent import views

app_name='Agent'

urlpatterns = [
     path("register-agent/", views.register_agent, name="register_agent"),
     path('agent_home/', views.agent_home, name='agent_home'),
     path("view-gas-products/", views.view_gas_products, name="view_gas_products"),
     path("book-gas-product/<int:gas_id>/",views. book_gas_product, name="book_gas_product"),
     path("my-bookings/", views.agent_bookings, name="agent_bookings"),
     path("payment/<int:booking_id>/", views.agent_payment_page, name="payment_page"),
     path("agent/bookings/", views.agent_view_user_bookings, name="agent_view_user_bookings"),
     path("stock-overview/", views.agent_stock_overview, name="agent_stock_overview"),
     path("profile/", views.agent_profile_view, name="agent_profile"),
    path("update-password/",views. update_password, name="update_password"),
]