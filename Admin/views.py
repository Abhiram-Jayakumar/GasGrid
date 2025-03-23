from django.shortcuts import redirect, render
from django.contrib import messages
from Admin.models import Gas
from Agent.models import Agent, GasBookAgent
from django.db.models import Sum

from User.models import UserBookGas

# Create your views here.

def admin_home(request):
    return render(request, 'Admin/admin_home.html')

#////////////////////////////////////////////////////////////////////////

def view_agents(request):
    agents = Agent.objects.all()
    return render(request, "Admin/view_agents.html", {"agents": agents})

def approve_agent(request, agent_id):
    agent = Agent.objects.get(id=agent_id)
    agent.agent_approved_status = 1
    agent.save()
    messages.success(request, f"Agent {agent.name} approved successfully.")
    return redirect("Admin:view_agents")

def reject_agent(request, agent_id):
    agent = Agent.objects.get(id=agent_id)
    agent.delete()
    messages.success(request, f"Agent {agent.name} rejected and removed.")
    return redirect("Admin:view_agents")


#///////////////////////////////////////////////////////////////////////////////////////

def add_gas(request):
    if request.method == "POST":
        name = request.POST.get('name')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        weight = request.POST.get('weight')
        retailer_price = request.POST.get('retailer_price')
        if not (name and category and quantity and retailer_price):
            messages.error(request, "All fields are required!")
            return redirect("Admin:add_gas")
        try:
            quantity = int(quantity)
            retailer_price = float(retailer_price)
            Gas.objects.create(
                name=name,
                category=category,
                quantity=quantity,
                initial_quantity=quantity,
                weight=weight,
                retailer_price=retailer_price
            )
            messages.success(request, "Gas Product added successfully!")
            return redirect("Admin:view_gas")
        except ValueError:
            messages.error(request, "Invalid data format!")
            return redirect("Admin:add_gas")
    return render(request, "Admin/add_gas.html")


def view_gas(request):
    gas = Gas.objects.all()
    return render(request, "Admin/view_gas.html", {"gas": gas})

#/////////////////////////////////////////////////////////////////////////

def update_booking_status(request, booking_id):
    if not request.user.is_staff:  # Ensure only admin can update
        messages.error(request, "Unauthorized access!")
        return redirect("Admin:dashboard")

    booking = GasBookAgent.objects.get(id=booking_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Pending", "Confirmed", "Delivered", "Canceled"]:
            booking.booking_status = new_status
            booking.save()
            messages.success(request, f"Booking status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")

    return redirect("Admin:manage_bookings")


#////////////////////////////////////////////////////////////////////////////////////////////////

def admin_view_agent_bookings(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        new_status = request.POST.get("status")

        try:
            booking = GasBookAgent.objects.get(id=booking_id)
            booking.booking_status = new_status
            booking.save()
            messages.success(request, f"Booking ID {booking_id} status updated to {new_status}.")
        except GasBookAgent.DoesNotExist:
            messages.error(request, "Invalid booking ID!")

    # Fetch all agent bookings
    agent_bookings = GasBookAgent.objects.all().select_related("agent", "gas_product")

    return render(request, "Admin/admin_view_agent_bookings.html", {"agent_bookings": agent_bookings})


#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def admin_stock_overview(request):
    gas_products = Gas.objects.all()
    stock_data = []

    for gas in gas_products:
        # Total quantity booked by agents
        total_sold_to_agents = GasBookAgent.objects.filter(gas_product=gas).aggregate(Sum("quantity"))["quantity__sum"] or 0

        # Total quantity sold by agents to users
        total_sold_by_agents = UserBookGas.objects.filter(gas_product=gas).aggregate(Sum("quantity"))["quantity__sum"] or 0

        # Remaining stock with agent
        remaining_stock_with_agents = total_sold_to_agents - total_sold_by_agents

        # Stock remaining in Admin inventory
        remaining_stock_admin = gas.quantity  

        stock_data.append({
            "gas": gas,
            "total_added": gas.initial_quantity,  # Admin's initially added stock
            "total_sold_to_agents": total_sold_to_agents,  # Total gas booked by agents
            "total_sold_by_agents": total_sold_by_agents,  # Total gas sold to users
            "remaining_stock_with_agents": remaining_stock_with_agents,  # Stock left with agents
            "remaining_stock_admin": remaining_stock_admin  # Stock left in Admin inventory
        })

    return render(request, "Admin/admin_stock_overview.html", {"stock_data": stock_data})