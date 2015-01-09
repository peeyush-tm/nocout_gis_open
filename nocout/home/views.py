from django.shortcuts import render


def home(request):
    """
    Renders the Home Page.
    """
    return render(request,'home/home.html')


def dashboard(request):
    """
    Renders the Dashboard Page.
    """
    return render(request,'home/dashboard.html')
