from django.shortcuts import render


def home(request):
    """
    Renders the Home Page.
    """
    return render(request,'home/home.html')
