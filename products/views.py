from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404

from products.models import Product
from orders.models import Order, OrderItem

import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
# =========================================================
# CUSTOMER LOGIN
# =========================================================

def customer_login(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:

            messages.error(
                request,
                "Invalid email or password."
            )

            return render(request, "login.html")

        user = authenticate(
            request,
            username=user.username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff:
                return redirect("admin_dashboard")

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid email or password."
        )

    return render(request, "login.html")


# =========================================================
# SIGNUP
# =========================================================

def signup(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(request, "signup.html")

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(request, "signup.html")

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return render(request, "signup.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )

        user.is_staff = False
        user.is_superuser = False

        user.save()

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "signup.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

def admin_login(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid admin username or password."
        )

    return render(
        request,
        "admin_login.html"
    )


# =========================================================
# CUSTOMER DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    user_orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_orders = user_orders.count()

    pending_orders = user_orders.filter(
        status__in=["Pending", "Placed"]
    ).count()

    delivered_orders = user_orders.filter(
        status="Delivered"
    ).count()

    context = {
        "user_orders": user_orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

# =========================================================
# ADMIN DASHBOARD
# =========================================================

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.shortcuts import render, redirect

from orders.models import Product, Order


@login_required
def admin_dashboard(request):

    # =====================================
    # SECURITY - ONLY ADMIN CAN ACCESS
    # =====================================

    if not request.user.is_staff:
        return redirect("dashboard")

    # =====================================
    # CUSTOMER SEARCH
    # =====================================

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
    )

    if search_query:

        customers = customers.filter(

            Q(username__icontains=search_query) |

            Q(email__icontains=search_query) |

            Q(first_name__icontains=search_query) |

            Q(last_name__icontains=search_query)

        )

    # =====================================
    # CUSTOMER ORDER COUNT
    # =====================================

    for customer in customers:

        customer.order_count = Order.objects.filter(
            user=customer
        ).count()

    # =====================================
    # TOTAL PRODUCTS
    # =====================================

    total_products = Product.objects.count()

    # =====================================
    # TOTAL ORDERS
    # =====================================

    total_orders = Order.objects.count()

    # =====================================
    # TOTAL CUSTOMERS
    # =====================================

    total_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    # =====================================
    # TOTAL SALES
    # CANCELLED ORDERS ARE NOT INCLUDED
    # =====================================

    total_sales = Order.objects.exclude(
        status="Cancelled"
    ).aggregate(

        total=Sum("total_amount")

    )["total"] or 0

    # =====================================
    # ALL PRODUCTS
    # =====================================

    products = Product.objects.all().order_by(
        "-created_at"
    )

    # =====================================
    # RECENT ORDERS
    # Optional - useful for dashboard later
    # =====================================

    recent_orders = Order.objects.select_related(
        "user"
    ).order_by(
        "-created_at"
    )[:5]

    # =====================================
    # CONTEXT
    # =====================================

    context = {

        "customers": customers,

        "products": products,

        "recent_orders": recent_orders,

        "search_query": search_query,

        "total_products": total_products,

        "total_orders": total_orders,

        "total_customers": total_customers,

        "total_sales": total_sales,

    }

    return render(
        request,
        "admin_dashboard.html",
        context
    )

# =========================================================
# ADMIN VIEW CUSTOMER ORDERS
# =========================================================

@login_required
def customer_orders(request, customer_id):

    if not request.user.is_staff:
        return redirect("dashboard")

    customer = get_object_or_404(
        User,
        id=customer_id
    )

    orders = (
        Order.objects
        .filter(user=customer)
        .prefetch_related("order_items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "customer_orders.html",
        {
            "customer": customer,
            "orders": orders,
        }
    )


# =========================================================
# LOGOUT
# =========================================================

def user_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")


# =========================================================
# ADD PRODUCT
# =========================================================

@staff_member_required
def add_product(request):

    if request.method == "POST":

        name = request.POST.get("name")
        category = request.POST.get("category")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")

        Product.objects.create(
            name=name,
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image
        )

        messages.success(
            request,
            "Product added successfully."
        )

        return redirect("products")

    categories = Product.CATEGORY_CHOICES

    return render(
        request,
        "add_product.html",
        {
            "categories": categories
        }
    )


# =========================================================
# PRODUCTS
# =========================================================
def products(request):

    search_query = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()

    products = Product.objects.all()

    if search_query:

        products = products.filter(

            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)

        )

    if category:

        products = products.filter(
            category__iexact=category
        )

    return render(
        request,
        "home.html",
        {
            "products": products,
            "search_query": search_query,
            "selected_category": category,
        }
    )

# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product.id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# =========================================================
# CART
# =========================================================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    cart_items = []

    invalid_product_ids = []

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id
            )

            quantity = int(quantity)

            item_total = (
                product.price * quantity
            )

            cart_items.append({

                "product": product,
                "quantity": quantity,
                "total": item_total

            })

        except Product.DoesNotExist:

            invalid_product_ids.append(
                product_id
            )

    for product_id in invalid_product_ids:

        cart_data.pop(
            product_id,
            None
        )

    request.session["cart"] = cart_data
    request.session.modified = True

    grand_total = sum(
        item["total"]
        for item in cart_items
    )

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "grand_total": grand_total,
        }
    )


# =========================================================
# CHECKOUT
# =========================================================

@login_required
def checkout(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    cart_items = []

    total = Decimal("0.00")

    for product_id, quantity in cart_data.items():

        try:

            product = Product.objects.get(
                id=product_id
            )

            quantity = int(quantity)

            item_total = (
                product.price * quantity
            )

            total += item_total

            cart_items.append({

                "product": product,
                "quantity": quantity,
                "total_price": item_total,

            })

        except Product.DoesNotExist:
            continue

    if not cart_items:

        messages.error(
            request,
            "No valid products found."
        )

        return redirect("cart")

    return render(
        request,
        "checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================================================
# PLACE ORDER
# =========================================================

# =========================================================
# PLACE ORDER
# =========================================================

@login_required
def place_order(request):

    if request.method != "POST":
        return redirect("checkout")

    cart = request.session.get("cart", {})

    if not cart:

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # -----------------------------------------
    # CUSTOMER DETAILS
    # -----------------------------------------

    name = request.POST.get(
        "full_name",
        ""
    ).strip()

    email = request.user.email

    phone = request.POST.get(
        "phone",
        ""
    ).strip()

    address = request.POST.get(
        "address",
        ""
    ).strip()

    city = request.POST.get(
        "city",
        ""
    ).strip()

    state = request.POST.get(
        "state",
        ""
    ).strip()

    pincode = request.POST.get(
        "pincode",
        ""
    ).strip()

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    if not name:

        messages.error(
            request,
            "Please enter your full name."
        )

        return redirect("checkout")

    if not email:

        messages.error(
            request,
            "Email is required."
        )

        return redirect("checkout")

    if not phone:

        messages.error(
            request,
            "Phone number is required."
        )

        return redirect("checkout")

    if not address:

        messages.error(
            request,
            "Address is required."
        )

        return redirect("checkout")

    if not city:

        messages.error(
            request,
            "City is required."
        )

        return redirect("checkout")

    if not state:

        messages.error(
            request,
            "State is required."
        )

        return redirect("checkout")

    if not pincode:

        messages.error(
            request,
            "PIN code is required."
        )

        return redirect("checkout")

    # -----------------------------------------
    # CREATE ORDER
    # -----------------------------------------

    try:

        with transaction.atomic():

            total_price = Decimal("0.00")

            valid_items = []

            for product_id, quantity in cart.items():

                try:

                    product = Product.objects.get(
                        id=product_id
                    )

                    quantity = int(quantity)

                    total_price += (
                        product.price * quantity
                    )

                    valid_items.append({

                        "product": product,
                        "quantity": quantity,

                    })

                except Product.DoesNotExist:

                    continue

            if not valid_items:

                messages.error(
                    request,
                    "No valid products found."
                )

                return redirect("cart")

            # CREATE ORDER

            order = Order.objects.create(

                user=request.user,

                name=name,

                email=email,

                phone=phone,

                address=address,

                city=city,

                state=state,

                pincode=pincode,

                total_amount=total_price,

                status="Pending"

            )

            order_items = []

            # CREATE ORDER ITEMS

            for item in valid_items:

                product = item["product"]

                order_item = OrderItem.objects.create(

                    order=order,

                    product=product,

                    quantity=item["quantity"],

                    price=product.price

                )

                order_items.append(
                    order_item
                )

    except Exception as e:

        print("ORDER ERROR:", str(e))

        messages.error(
            request,
            f"Unable to place order: {str(e)}"
        )

        return redirect("checkout")

    # =====================================================
    # CREATE EMAIL PRODUCTS HTML WITH EMBEDDED IMAGES
    # =====================================================

    items_html = ""

    email_images = []

    for index, item in enumerate(order_items):

        product = item.product

        image_cid = f"product_image_{index}"

        # -----------------------------------------
        # EMBED PRODUCT IMAGE
        # -----------------------------------------

        if product.image:

            try:

                image_path = product.image.path

                if os.path.exists(image_path):

                    with open(
                        image_path,
                        "rb"
                    ) as image_file:

                        image = MIMEImage(
                            image_file.read()
                        )

                        image.add_header(
                            "Content-ID",
                            f"<{image_cid}>"
                        )

                        image.add_header(
                            "Content-Disposition",
                            "inline",
                            filename=os.path.basename(
                                product.image.name
                            )
                        )

                        email_images.append(
                            image
                        )

                    image_html = f"""

                    <img
                        src="cid:{image_cid}"
                        alt="{product.name}"
                        style="
                            width:120px;
                            height:120px;
                            object-fit:contain;
                            border-radius:10px;
                        "
                    >

                    """

                else:

                    image_html = """

                    <div style="
                        width:120px;
                        height:120px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        color:#777;
                    ">
                        No Image
                    </div>

                    """

            except Exception as image_error:

                print(
                    "IMAGE ERROR:",
                    str(image_error)
                )

                image_html = """

                <div style="
                    width:120px;
                    height:120px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#777;
                ">
                    No Image
                </div>

                """

        else:

            image_html = """

            <div style="
                width:120px;
                height:120px;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#777;
            ">
                No Image
            </div>

            """

        # -----------------------------------------
        # PRODUCT HTML
        # -----------------------------------------

        items_html += f"""

        <div style="
            border:1px solid #dddddd;
            border-radius:10px;
            padding:15px;
            margin-bottom:15px;
            display:flex;
            align-items:center;
        ">

            <div style="
                margin-right:20px;
            ">

                {image_html}

            </div>

            <div>

                <h3 style="
                    margin:0 0 10px 0;
                ">
                    {product.name}
                </h3>

                <p>
                    Quantity: {item.quantity}
                </p>

                <p>
                    Price: ₹{item.price}
                </p>

            </div>

        </div>

        """

    # =====================================================
    # HTML EMAIL
    # =====================================================

    html_message = f"""

    <!DOCTYPE html>

    <html>

    <body style="
        font-family:Arial, sans-serif;
        background:#f5f5f5;
        padding:20px;
    ">

        <div style="
            max-width:650px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:15px;
        ">

            <h1 style="
                text-align:center;
                color:#2563eb;
            ">
                🛒 E-Shop
            </h1>

            <h2>
                Order Placed Successfully 🎉
            </h2>

            <p>

                Hello

                <strong>
                    {request.user.first_name or request.user.username}
                </strong>,

            </p>

            <p>
                Thank you for shopping with E-Shop.
            </p>

            <hr>

            <p>
                <strong>Order ID:</strong>
                #{order.id}
            </p>

            <p>
                <strong>Status:</strong>
                {order.status}
            </p>

            <p>
                <strong>Total Amount:</strong>
                ₹{order.total_amount}
            </p>

            <h2>
                Ordered Products
            </h2>

            {items_html}

            <h2 style="
                text-align:right;
                color:#2563eb;
            ">
                Total: ₹{order.total_amount}
            </h2>

            <hr>

            <p style="
                text-align:center;
            ">
                Thank you for choosing E-Shop! ❤️
            </p>

        </div>

    </body>

    </html>

    """

    # =====================================================
    # TEXT EMAIL
    # =====================================================

    text_message = f"""

Hello {request.user.first_name or request.user.username},

Your order has been placed successfully.

Order ID: #{order.id}

Status: {order.status}

Total Amount: ₹{order.total_amount}

Thank you for shopping with E-Shop!

"""

    # =====================================================
    # SEND EMAIL WITH EMBEDDED IMAGES
    # =====================================================

    try:

        customer_email = request.user.email

        email_message = EmailMultiAlternatives(

            subject=f"E-Shop - Order #{order.id} Placed Successfully",

            body=text_message,

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[customer_email],

        )

        # ADD HTML EMAIL

        email_message.attach_alternative(

            html_message,

            "text/html"

        )

        # -----------------------------------------
        # ATTACH PRODUCT IMAGES
        # -----------------------------------------

        for image in email_images:

            email_message.attach(
                image
            )

        # SEND EMAIL

        result = email_message.send(
            fail_silently=False
        )

        print(
            "EMAIL SENT RESULT:",
            result
        )

    except Exception as e:

        print(
            "EMAIL ERROR:",
            str(e)
        )

    # =====================================================
    # CLEAR CART
    # =====================================================

    request.session["cart"] = {}

    request.session.modified = True

    messages.success(

        request,

        f"Order #{order.id} placed successfully!"

    )

    return redirect(

        "order_success",

        order_id=order.id

    )
# =========================================================
# ORDER SUMMARY
# =========================================================

@login_required
def order_summary(request):

    orders = (

        Order.objects

        .filter(user=request.user)

        .prefetch_related(
            "order_items__product"
        )

        .order_by("-created_at")

    )

    total_orders = orders.count()

    cancelled_orders = orders.filter(
        status="Cancelled"
    ).count()

    active_orders = orders.exclude(
        status="Cancelled"
    ).count()

    delivered_orders = orders.filter(
        status="Delivered"
    ).count()

    total_sales = sum(

        order.total_amount

        for order in orders.exclude(
            status="Cancelled"
        )

    )

    context = {

        "orders": orders,

        "total_orders": total_orders,

        "active_orders": active_orders,

        "cancelled_orders": cancelled_orders,

        "delivered_orders": delivered_orders,

        "total_sales": total_sales,

    }

    return render(

        request,

        "order_summary.html",

        context

    )


# =========================================================
# ORDERS
# =========================================================

@login_required
def orders(request):

    customer_orders = (

        Order.objects

        .filter(user=request.user)

        .prefetch_related(
            "order_items__product"
        )

        .order_by("-created_at")

    )

    return render(

        request,

        "orders.html",

        {
            "orders": customer_orders
        }

    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(

        Order.objects.prefetch_related(
            "order_items__product"
        ),

        id=order_id,

        user=request.user

    )

    return render(

        request,

        "order_success.html",

        {
            "order": order
        }

    )


# =========================================================
# CANCEL ORDER
# =========================================================

@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )

    if request.method == "POST":

        if order.status in [

            "Pending",

            "Placed",

            "Confirmed"

        ]:

            order.status = "Cancelled"

            order.save()

            messages.success(

                request,

                "Order cancelled successfully."

            )

    return redirect(
        "orders"
    )


# =========================================================
# RETURN ORDER
# =========================================================

@login_required
def return_order(request, order_id):

    order = get_object_or_404(

        Order,

        id=order_id,

        user=request.user

    )

    if request.method == "POST":

        if order.status == "Delivered":

            order.status = "Return Requested"

            order.save()

            messages.success(

                request,

                "Return request submitted successfully."

            )

    return redirect(
        "orders"
    )


# =========================================================
# INCREASE QUANTITY
# =========================================================

def increase_quantity(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# DECREASE QUANTITY
# =========================================================

def decrease_quantity(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        if cart[product_id] > 1:

            cart[product_id] -= 1

        else:

            del cart[product_id]

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart")


# =========================================================
# ADMIN ORDERS
# =========================================================

@login_required
def admin_orders(request):

    if not request.user.is_staff:
        return redirect("dashboard")

    all_orders = (

        Order.objects

        .select_related("user")

        .prefetch_related(
            "order_items__product"
        )

        .order_by("-created_at")

    )

    return render(

        request,

        "admin_orders.html",

        {
            "orders": all_orders
        }

    )


# =========================================================
# ADMIN CUSTOMER ORDERS
# =========================================================

@login_required
def admin_customer_orders(request, customer_id):

    if not request.user.is_staff:
        return redirect("dashboard")

    customer = get_object_or_404(

        User,

        id=customer_id,

        is_staff=False

    )

    customer_orders = (

        Order.objects

        .filter(user=customer)

        .prefetch_related(
            "order_items__product"
        )

        .order_by("-created_at")

    )

    return render(

        request,

        "admin_customer_orders.html",

        {

            "customer": customer,

            "orders": customer_orders

        }

    )


# =========================================================
# UPDATE PROFILE
# =========================================================
@login_required
def update_profile(request):

    user = request.user

    if request.method == "POST":

        user.first_name = request.POST.get(
            "first_name",
            ""
        )

        user.last_name = request.POST.get(
            "last_name",
            ""
        )

        user.email = request.POST.get(
            "email",
            ""
        )

        user.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        # ADMIN
        if user.is_staff:
            return redirect("admin_dashboard")

        # CUSTOMER
        return redirect("dashboard")

    return render(
        request,
        "update_profile.html"
    )

# =========================================================
# TOGGLE WISHLIST
# =========================================================

def toggle_wishlist(request, product_id):

    wishlist = request.session.get(
        "wishlist",
        []
    )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product_id in wishlist:

        wishlist.remove(product_id)

    else:

        wishlist.append(product_id)

    request.session["wishlist"] = wishlist

    request.session.modified = True

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home"
        )
    )


# =========================================================
# WISHLIST
# =========================================================

def wishlist(request):

    wishlist_ids = request.session.get(
        "wishlist",
        []
    )

    products_list = Product.objects.filter(
        id__in=wishlist_ids
    )

    return render(

        request,

        "wishlist.html",

        {

            "products": products_list,

            "wishlist_ids": wishlist_ids

        }

    )


# =========================================================
# REMOVE FROM WISHLIST
# =========================================================

def remove_from_wishlist(request, product_id):

    wishlist = request.session.get(
        "wishlist",
        []
    )

    if product_id in wishlist:

        wishlist.remove(product_id)

    request.session["wishlist"] = wishlist

    request.session.modified = True

    return redirect(
        "wishlist"
    )

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
from django.utils.html import escape
import os

@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order.status = "Cancelled"
    order.save()

    items = order.order_items.all()

    subject = f"Order #{order.id} Cancelled"

    product_html = ""
    image_attachments = []

    for index, item in enumerate(items):

        image_cid = f"product_image_{order.id}_{index}"

        if item.product.image:

            product_html += f"""
            <div style="border:1px solid #dddddd; padding:15px; margin:15px 0; border-radius:8px;">

                <img src="cid:{image_cid}"
                     width="150"
                     style="display:block; margin-bottom:10px;">

                <h3>{escape(item.product.name)}</h3>

                <p><b>Quantity:</b> {item.quantity}</p>

                <p><b>Price:</b> ₹{item.price}</p>

            </div>
            """

            image_attachments.append(
                (image_cid, item.product.image.path)
            )

        else:

            product_html += f"""
            <div style="border:1px solid #dddddd; padding:15px; margin:15px 0;">

                <h3>{escape(item.product.name)}</h3>

                <p><b>Quantity:</b> {item.quantity}</p>

                <p><b>Price:</b> ₹{item.price}</p>

            </div>
            """

    html_message = f"""
    <html>
    <body style="font-family:Arial, sans-serif;">

        <h2>Hello {escape(request.user.username)},</h2>

        <p>
            Your order has been
            <b style="color:red;">Cancelled</b>.
        </p>

        <h3>Order ID: #{order.id}</h3>

        {product_html}

        <h2>Total Amount: ₹{order.total_amount}</h2>

        <p>Thank you for shopping with us.</p>

    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body="Your order has been cancelled.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email]
    )

    email.attach_alternative(html_message, "text/html")

    for image_cid, image_path in image_attachments:

        try:
            with open(image_path, "rb") as image_file:

                image = MIMEImage(image_file.read())

                image.add_header(
                    "Content-ID",
                    f"<{image_cid}>"
                )

                image.add_header(
                    "Content-Disposition",
                    "inline",
                    filename=os.path.basename(image_path)
                )

                email.attach(image)

        except Exception as e:
            print("Image email error:", e)

    email.send(fail_silently=False)

    return redirect("orders")

@login_required
def return_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Update order status
    order.status = "Return Requested"
    order.save()

    items = order.order_items.all()

    subject = f"Return Request - Order #{order.id}"

    product_html = ""
    image_attachments = []

    # Get all products in the order
    for index, item in enumerate(items):

        image_cid = f"product_image_{order.id}_{index}"

        if item.product.image:

            product_html += f"""
            <div style="
                border: 1px solid #dddddd;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
            ">

                <img src="cid:{image_cid}"
                     width="150"
                     style="
                        display: block;
                        margin-bottom: 10px;
                        border-radius: 5px;
                     ">

                <h3>{escape(item.product.name)}</h3>

                <p>
                    <b>Quantity:</b> {item.quantity}
                </p>

                <p>
                    <b>Price:</b> ₹{item.price}
                </p>

            </div>
            """

            image_attachments.append(
                (image_cid, item.product.image.path)
            )

        else:

            product_html += f"""
            <div style="
                border: 1px solid #dddddd;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
            ">

                <h3>{escape(item.product.name)}</h3>

                <p>
                    <b>Quantity:</b> {item.quantity}
                </p>

                <p>
                    <b>Price:</b> ₹{item.price}
                </p>

            </div>
            """

    # HTML Email
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">

        <h2>Hello {escape(request.user.username)},</h2>

        <p>
            Your return request has been submitted successfully.
        </p>

        <h3>Order ID: #{order.id}</h3>

        {product_html}

        <h2>
            Total Amount: ₹{order.total_amount}
        </h2>

        <p>
            Status:
            <b>Return Requested</b>
        </p>

        <p>
            We will review your return request and update you soon.
        </p>

        <br>

        <p>
            Thank you for shopping with us.
        </p>

    </body>
    </html>
    """

    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body="Your return request has been submitted successfully.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email]
    )

    # Attach HTML
    email.attach_alternative(
        html_message,
        "text/html"
    )

    # Attach product images inline
    for image_cid, image_path in image_attachments:

        try:

            with open(image_path, "rb") as image_file:

                image = MIMEImage(
                    image_file.read()
                )

                image.add_header(
                    "Content-ID",
                    f"<{image_cid}>"
                )

                image.add_header(
                    "Content-Disposition",
                    "inline",
                    filename=os.path.basename(image_path)
                )

                email.attach(image)

        except Exception as e:

            print(
                "Product image email error:",
                e
            )

    # Send email
    email.send(
        fail_silently=False
    )

    return redirect("orders")