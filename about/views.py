from django.shortcuts import render

# Create your views here.
def about(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            dashboard_url = 'admin_dashboard'
        else:
            dashboard_url = 'dashboard'
    else:
        dashboard_url = 'login'

    return render(request, 'about.html', {
        'dashboard_url': dashboard_url
    })