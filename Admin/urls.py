from django.urls import path
from Admin import views

app_name = 'Admin'

urlpatterns = [
    path('admin_home/', views.admin_home, name='admin_home'),
    path("view-agents/",views. view_agents, name="view_agents"),
    path("approve-agent/<int:agent_id>/", views.approve_agent, name="approve_agent"),
    path("reject-agent/<int:agent_id>/", views.reject_agent, name="reject_agent"),
    path("add-gas/",views.add_gas, name="add_gas"),
    path("view-gas/",views.view_gas, name="view_gas"),
    path("admin/agent-bookings/", views.admin_view_agent_bookings, name="admin_view_agent_bookings"),
    path("stock-overview/",views.admin_stock_overview, name="admin_stock_overview"),
]