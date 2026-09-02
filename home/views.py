from django.shortcuts import render
from products.models import Product


def home(request):

    products = Product.objects.all()

    search_query = request.GET.get("search", "")

    selected_category = request.GET.get("category", "")

    # SEARCH

    if search_query:

        products = products.filter(
            name__icontains=search_query
        )


    # CATEGORY FILTER

    if selected_category:

        products = products.filter(
            category=selected_category
        )


    # WISHLIST

    wishlist_ids = request.session.get(
        "wishlist",
        []
    )


    return render(
        request,
        "home.html",
        {
            "products": products,
            "search_query": search_query,
            "selected_category": selected_category,
            "wishlist_ids": wishlist_ids
        }
    )