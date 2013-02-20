from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    password = forms.CharField(max_length=20)

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('home'))
                else:
                    messages.error(request, 'User account not active.')
                    return HttpResponseRedirect(reverse('login_page'))
            else:
                messages.error(request, 'Login failed!')
                return HttpResponseRedirect(reverse('login_page'))
    else:
        form = LoginForm()
    args = {'form': form}
    if 'next' not in request.GET:
        args['next'] = None
    else:
        args['next'] = request.GET['next']
    return render(request, 'accounts/login.html', args)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))