from django.urls import path
from User import views

app_name = 'User'

urlpatterns = [
    path('index/', views.index, name='index'),
    path("register-user/", views.register_user, name="register_user"),
    path("login/", views.login, name="login"),
    path('user_home/', views.user_home, name='user_home'),
    path("available-gas/", views.view_agent_gas, name="view_agent_gas"),
    path("book-gas/<int:gas_id>/<int:agent_id>/", views.user_book_gas, name="user_book_gas"),
    path("my-bookings/", views.user_booking_details, name="user_booking_details"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),
    path("profile/",views. user_profile, name="user_profile"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("update-password/", views.update_password, name="update_password"),
]