from django.shortcuts import redirect, render
from django.contrib import messages

from Admin.models import Admintable, Gas
from Agent.models import Agent, GasBookAgent
from User.models import User, UserBookGas
# Create your views here.


def index(request):
    return render(request, 'User/index.html')

#/////////////////////////////////////////////////////////////////////////////////////////

def register_user(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        address = request.POST.get("address", "")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        password = request.POST["password"]

        # File upload
        profile_image = request.FILES.get("profile_image")
        idproof_User = request.FILES.get("idproof_User")

        # Validate location
        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            messages.error(request, "Invalid location coordinates")
            return render(request, "user_register.html")

        # Save to database
        user = User(
            name=name,
            email=email,
            phone_number=phone_number,
            address=address,
            latitude=lat,
            longitude=lon,
            password=password,  # Storing in plain text (not recommended)
            profile_image=profile_image,
            idproof_User=idproof_User
        )
        user.save()
        messages.success(request, "User registered successfully")
        return redirect("User:index")

    return render(request, "User/user_register.html")

#/////////////////////////////////////////////////////////////////////////////////////////

def login(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        Ulogin=User.objects.filter(email=email,password=password).count()
        Alogin=Admintable.objects.filter(email=email,password=password).count()
        Aglogin=Agent.objects.filter(email=email,password=password,agent_approved_status=True).count()
        if Ulogin > 0:
            uadmin=User.objects.get(email=email,password=password)
            request.session['uid']=uadmin.id
            return redirect('User:user_home')
        elif Alogin > 0:
            aadmin=Admintable.objects.get(email=email,password=password)
            request.session['aid']=aadmin.id
            return redirect('Admin:admin_home')
        elif Aglogin > 0:
            madmin=Agent.objects.get(email=email,password=password,agent_approved_status=1)
            request.session['agid']=madmin.id
            return redirect('Agent:agent_home')
        else:
            error="Invalid Credentials!!"
            return render(request,"User/login.html",{'ERR':error})
    else:
        return render(request, "User/login.html")

#/////////////////////////////////////////////////////////////////////////////////////////

def user_home(request):
    return render(request, "User/user_home.html")


#////////////////////////////////////////////////////////////////////////////////

def user_book_gas(request, gas_id, agent_id):
    if 'uid' not in request.session:  
        messages.error(request, "You must be logged in to book gas!")
        return redirect("User:user_login")

    user = User.objects.get(id=request.session['uid'])  # Get logged-in user
    agent = Agent.objects.get(id=agent_id)
    gas_product = Gas.objects.get(id=gas_id)
    agent_booking = GasBookAgent.objects.filter(agent=agent, gas_product=gas_product).first()

    if not agent_booking or agent_booking.quantity <= 0:
        messages.error(request, "This gas product is currently unavailable from this agent.")
        return redirect("User:view_agent_gas")

    if request.method == "POST":
        requested_quantity = int(request.POST.get("quantity"))

        if requested_quantity <= 0:
            messages.error(request, "Quantity must be greater than zero.")
            return redirect("User:user_book_gas", gas_id=gas_product.id, agent_id=agent.id)

        if requested_quantity > agent_booking.quantity:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect("User:user_book_gas", gas_id=gas_product.id, agent_id=agent.id)

        # Reduce the booked quantity from the agent's stock
        agent_booking.quantity -= requested_quantity
        agent_booking.save()

        # Create a user booking record with 'Pending' payment status
        booking = UserBookGas.objects.create(
            user=user,  
            agent=agent,
            gas_product=gas_product,
            quantity=requested_quantity,
            booking_status="Confirmed",
            payment_status="Pending"
        )

        messages.success(request, f"Successfully booked {requested_quantity} units of {gas_product.name} from {agent.name}. Proceed to payment.")
        return redirect("User:payment_page", booking_id=booking.id)  # Redirect to Payment Page

    return render(request, "User/user_book_gas.html", {
        "agent": agent,
        "gas_product": gas_product,
        "agent_booking": agent_booking
    })


    
#///////////////////////////////////////////////////////////////////////////////////////////////////

def view_agent_gas(request):
    agent_bookings = GasBookAgent.objects.filter(quantity__gt=0).select_related("gas_product", "agent")
    return render(request, "User/view_agent_gas.html", {"agent_bookings": agent_bookings})

#////////////////////////////////////////////////////////////////////////////////////////////////////////////

def user_booking_details(request):
    if 'uid' not in request.session:  
        messages.error(request, "You must be logged in to view your bookings!")
        return redirect("User:user_login")

    user_id = request.session['uid']
    user = User.objects.get(id=user_id)  

    # Fetch bookings using the correct user reference
    bookings = UserBookGas.objects.filter(user=user)

    if not bookings.exists():
        messages.info(request, "No bookings found.")

    return render(request, "User/user_booking_details.html", {"bookings": bookings})

#////////////////////////////////////////////////////////////////////////////////////////////////////////

def payment_page(request, booking_id):
    booking = UserBookGas.objects.get(id=booking_id)

    # Calculate total price in the backend
    total_price = booking.quantity * booking.gas_product.retailer_price  

    if request.method == "POST":
        # Assume payment is successful (For real payments, integrate Razorpay/Stripe)
        booking.payment_status = "Paid"
        booking.save()
        messages.success(request, "Payment successful! Your booking is now complete.")
        return redirect("User:user_booking_details")

    return render(request, "User/payment_page.html", {"booking": booking, "total_price": total_price})

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def user_profile(request):
    if 'uid' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect("User:login")

    user = User.objects.get(id=request.session['uid'])
    return render(request, "User/user_profile.html", {"user": user})


def update_profile(request):
    if 'uid' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect("User:login")

    user = User.objects.get(id=request.session['uid'])

    if request.method == "POST":
        user.name = request.POST.get("name")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")

        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("User:user_profile")

    return render(request, "User/update_profile.html", {"user": user})


def update_password(request):
    if 'uid' not in request.session:
        messages.error(request, "You must be logged in!")
        return redirect("User:login")

    user = User.objects.get(id=request.session['uid'])

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if user.password != current_password:
            messages.error(request, "Current password is incorrect.")
            return redirect("User:update_password")

        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect("User:update_password")

        user.password = new_password  # ❗️ Storing in plain text (not recommended)
        user.save()
        messages.success(request, "Password updated successfully.")
        return redirect("User:user_profile")

    return render(request, "User/update_password.html")