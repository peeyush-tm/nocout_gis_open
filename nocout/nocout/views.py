from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect

# from forms import MyRegistrationForm


@csrf_protect
def login(request):
    return render(request, 'login.html')


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # check whether username & password exist in database
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        # if you have an authenticated user you want to attach to the current session
        auth.login(request, user)
        return HttpResponseRedirect('/loggedin/')
    else:
        return HttpResponseRedirect('/invalid/')


def loggedin(request):
    # return render_to_response('loggedin.html', {'full_name' : request.user.username})
    return render(request,'loggedin.html',{'full_name' : request.user.username})

def invalid_login(request):
    return render(request,'invalid_login.html')


def logout(request):
    auth.logout(request)
    return render(request,'logout.html')