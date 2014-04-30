from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib import auth
# from forms import MyRegistrationForm

def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)


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
    return render_to_response('loggedin.html', {'username': request.user.username})


def invalid_login(request):
    return render_to_response('invalid_login.html')


def logout(request):
    auth.logout(request)
    return render_to_response('logout.html') 