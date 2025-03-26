from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from Admin.models import Gas
from Agent.models import Agent, GasBookAgent, GasProduct
from User.models import UserBookGas, UserProductBooking
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models import Sum
from django.core.files.storage import default_storage
from django.contrib import messages
from decimal import Decimal


def register_agent(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        license_number = request.POST["license_number"]
        agency_name = request.POST["agency_name"]
        agency_start_year = request.POST["agency_start_year"]
        address = request.POST.get("address", "")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        password = request.POST["password"]
        agent_image = request.FILES.get("agent_image")
        agent_idproof = request.FILES.get("agent_idproof")
        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            messages.error(request, "Invalid location coordinates")
            return render(request, "agent_register.html")
        agent = Agent(
            name=name,
            email=email,
            phone_number=phone_number,
            license_number=license_number,
            agency_name=agency_name,
            agency_start_year=agency_start_year,
            address=address,
            latitude=lat,
            longitude=lon,
            password=password, 
            agent_image=agent_image,
            agent_idproof=agent_idproof,
        )
        agent.save()
        messages.success(request, "Agent registered successfully")
        return redirect("User:index")

    return render(request, "Agent/agent_register.html")

#/////////////////////////////////////////////////////////////////////////////////////////

def agent_home(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect("User:login")

    agent = Agent.objects.get(id=request.session['agid'])
    return render(request, 'Agent/agent_home.html', {"agent": agent})

#//////////////////////////////////////////////////////////////////////////////////////////


def view_gas_products(request):
    if 'agid' not in request.session:  
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")
    gas_products = Gas.objects.all()
    return render(request, "Agent/view_gas_products.html", {"gas_products": gas_products})

#////////////////////////////////////////////////////////////////////////////////////////////

def book_gas_product(request, gas_id):
    if 'agid' not in request.session:  
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")

    agent = Agent.objects.get(id=request.session['agid']) 
    gas_product = Gas.objects.get(id=gas_id)

    if request.method == "POST":
        requested_quantity = int(request.POST.get('quantity'))   

        if requested_quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect("Agent:book_gas_product", gas_id=gas_product.id)

        if requested_quantity > gas_product.quantity:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect("Agent:book_gas_product", gas_id=gas_product.id)
        
        total_price = requested_quantity * gas_product.retailer_price  

        gas_product.quantity -= requested_quantity
        gas_product.save()

        GasBookAgent.objects.create(
            agent=agent,
            gas_product=gas_product,
            quantity=requested_quantity,
            total_price=total_price
        )

        messages.success(request, f"Successfully booked {requested_quantity} units of {gas_product.name}.")
        return redirect("Agent:agent_bookings")

    return render(request, "Agent/book_gas_product.html", {"gas_product": gas_product})

#///////////////////////////////////////////////////////////////////////////////////////////////////////

def agent_bookings(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")

    agent = Agent.objects.get(id=request.session['agid'])
    bookings = GasBookAgent.objects.filter(agent=agent).select_related("gas_product")

    return render(request, "Agent/agent_bookings.html", {"bookings": bookings})

#//////////////////////////////////////////////////////////////////////////////////////////////////////


def agent_payment_page(request, booking_id):
    booking = GasBookAgent.objects.get(id=booking_id)

    if request.method == "POST":
        booking.payment_status = "Paid"
        booking.booking_status = "Confirmed"  
        booking.save()
        messages.success(request, "Payment successful! Your booking is now confirmed.")
        return redirect("Agent:agent_bookings")

    return render(request, "Agent/agent_payment_page.html", {"booking": booking})


#///////////////////////////////////////////////////////////////////////////////////////////

def agent_view_user_bookings(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("User:login")  
    agent = Agent.objects.get(id=request.session['agid'])

    user_bookings = (
        UserBookGas.objects.filter(agent=agent)
        .select_related("user", "gas_product")
        .annotate(
            total_price=ExpressionWrapper(
                F("quantity") * F("gas_product__retailer_price"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
    )

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        new_status = request.POST.get("status")

        try:
            booking = UserBookGas.objects.get(id=booking_id, agent=agent)
            booking.booking_status = new_status
            booking.save()
            messages.success(request, f"Booking ID {booking_id} status updated to {new_status}.")
        except UserBookGas.DoesNotExist:
            messages.error(request, "Invalid booking ID!")

        return redirect("Agent:agent_view_user_bookings") 
    return render(request, "Agent/agent_view_user_bookings.html", {"user_bookings": user_bookings})


#/////////////////////////////////////////////////////////////////////////////////////////

def agent_stock_overview(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")

    agent_id = request.session['agid']
    
    agent_gas_bookings = GasBookAgent.objects.filter(agent_id=agent_id).select_related("gas_product")

    stock_data = []

    for booking in agent_gas_bookings:
        gas = booking.gas_product

        total_booked_from_admin = GasBookAgent.objects.filter(agent=booking.agent, gas_product=gas).aggregate(Sum("quantity"))["quantity__sum"] or 0

        total_sold_to_users = UserBookGas.objects.filter(agent=booking.agent, gas_product=gas).aggregate(Sum("quantity"))["quantity__sum"] or 0

        remaining_stock = total_booked_from_admin - total_sold_to_users

        stock_data.append({
            "gas": gas,
            "total_booked": total_booked_from_admin,
            "total_sold": total_sold_to_users,
            "remaining_stock": remaining_stock
        })

    return render(request, "Agent/agent_stock_overview.html", {"stock_data": stock_data})


#////////////////////////////////////////////////////////////////////////////////////////////////////

def agent_profile_view(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")

    agent_id = request.session['agid']
    agent = Agent.objects.get(id=agent_id)

    if request.method == "POST":
        agent.name = request.POST.get("name")
        agent.email = request.POST.get("email")
        agent.phone_number = request.POST.get("phone_number")
        agent.license_number = request.POST.get("license_number")
        agent.agency_name = request.POST.get("agency_name")
        agent.agency_start_year = request.POST.get("agency_start_year")
        agent.address = request.POST.get("address")
        agent.latitude = request.POST.get("latitude") or None
        agent.longitude = request.POST.get("longitude") or None

        if "agent_image" in request.FILES:
            if agent.agent_image:
                default_storage.delete(agent.agent_image.path) 
            agent.agent_image = request.FILES["agent_image"]

        if "agent_idproof" in request.FILES:
            if agent.agent_idproof:
                default_storage.delete(agent.agent_idproof.path) 
            agent.agent_idproof = request.FILES["agent_idproof"]

        agent.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("Agent:agent_profile")

    return render(request, "Agent/agent_profile.html", {"agent": agent})

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def update_password(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:agent_login")

    agent_id = request.session['agid']
    agent = Agent.objects.get(id=agent_id)

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if agent.password != current_password:
            messages.error(request, "Current password is incorrect.")
            return redirect("Agent:update_password")

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect("Agent:update_password")

        agent.password = new_password
        agent.save()
        messages.success(request, "Password updated successfully.")
        return redirect("Agent:agent_profile")

    return render(request, "Agent/update_password.html")

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////

def add_gas_product(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:login")

    agent = Agent.objects.get(id=request.session['agid']) 

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        quantity_available = request.POST.get("quantity_available")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        if not all([name, description, quantity_available, price]):
            messages.error(request, "All fields except the image are required!")
            return redirect("Agent:add_gas_product")

        gas_product = GasProduct(
            agent=agent,
            name=name,
            description=description,
            quantity_available=quantity_available,
            price=price,
            image=image
        )
        gas_product.save()

        messages.success(request, "Gas product added successfully!")
        return redirect("Agent:agent_added_products")

    return render(request, "Agent/add_gas_product.html")

#//////////////////////////////////////////////////////////////////////////////////////////////


def agent_added_products(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:login")

    agent = Agent.objects.get(id=request.session['agid'])
    gas_products = GasProduct.objects.filter(agent=agent)

    return render(request, "Agent/agent_addedprocts.html", {"gas_products": gas_products})

#////////////////////////////////////////////////////////////////////////////////////////////

def agent_product_bookings(request):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:login")

    agent = Agent.objects.get(id=request.session['agid'])
    bookings = UserProductBooking.objects.filter(agent=agent)
   

    return render(request, "Agent/agent_product_bookings.html", {"bookings": bookings})


#///////////////////////////////////////////////////////////////////////////////////////////////////

def edit_gas_product(request, product_id):
    if 'agid' not in request.session:
        messages.error(request, "You must be logged in as an agent!")
        return redirect("Agent:login")

    product = get_object_or_404(GasProduct, id=product_id, agent_id=request.session['agid'])

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        
        quantity = request.POST.get("quantity")
        if quantity is None or quantity.strip() == "":
            messages.error(request, "Quantity cannot be empty!")
            return redirect("Agent:edit_gas_product", product_id=product.id)
        try:
            product.quantity_available = int(quantity)
        except ValueError:
            messages.error(request, "Quantity must be a number!")
            return redirect("Agent:edit_gas_product", product_id=product.id)

        price = request.POST.get("price")
        try:
            product.price = Decimal(price)
        except:
            messages.error(request, "Invalid price format!")
            return redirect("Agent:edit_gas_product", product_id=product.id)

        if "image" in request.FILES:
            product.image = request.FILES["image"]

        product.save(update_fields=["name", "description", "quantity_available", "price", "image"])

        messages.success(request, "Product updated successfully!")
        return redirect("Agent:agent_added_products")  

    return render(request, "Agent/agent_edit_product.html", {"product": product})