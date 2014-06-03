from actstream import action
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User

@csrf_protect
def login(request):
    return render(request, 'nocout/login.html')


def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # check whether username & password exist in database
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        # if you have an authenticated user you want to attach to the current session
        auth.login(request, user)
        action.send(request.user, verb=u'username : %s loggedin from server name: %s, server port: %s'\
                                       %( username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
        return HttpResponseRedirect('/loggedin/')
    else:
        action.send(User.objects.get(pk=1),
        verb=u'invalid loggedin using username : %s from server name: %s, server port: %s' %( username,
                                                    request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
        return HttpResponseRedirect('/invalid/')


def loggedin(request):
    # return render_to_response('loggedin.html', {'full_name' : request.user.username})
    return HttpResponseRedirect('/home/')


def invalid_login(request):
    return render(request,'nocout/login.html')


def logout(request):
    auth.logout(request)
    return render(request,'nocout/login.html')

