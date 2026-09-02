from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order, OrderItem
@login_required(login_url='login')
@login_required
def dashboard(request):

    # ADMIN DASHBOARD
    if request.user.is_staff:

        total_orders = Order.objects.count()

        pending_orders = Order.objects.filter(
            status="Pending"
        ).count()

        delivered_orders = Order.objects.filter(
            status="Delivered"
        ).count()

        cancelled_orders = Order.objects.filter(
            status="Cancelled"
        ).count()

        total_customers = User.objects.filter(
            is_staff=False
        ).count()

        context = {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "total_customers": total_customers,
        }

        return render(
            request,
            "admin_dashboard.html",
            context
        )

    # CUSTOMER DASHBOARD

    user_orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_orders = user_orders.count()

    pending_orders = user_orders.filter(
        status="Pending"
    ).count()

    delivered_orders = user_orders.filter(
        status="Delivered"
    ).count()

    cancelled_orders = user_orders.filter(
        status="Cancelled"
    ).count()

    context = {
        "user_orders": user_orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
    }

    return render(
        request,
        "dashboard.html",
        context
    )