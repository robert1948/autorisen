
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate , login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterUserForm


def login_user(request):
    return render(request,'authenticate/login.html',{})




def logout_user(request):
    logout(request)
    messages.success(request,('You have been logged out...'))
    return redirect('home')  

def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)  # use your custom form
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:  # check if user is successfully authenticated
                login(request, user)
                messages.success(request, f'New User Account Created: {username}')
                return redirect('home')
            else:
                messages.error(request, 'There was an error creating your account. Please try again.')
        else:
            messages.error(request, 'There was an error with your registration form. Please correct the errors and try again.')
    else:
        form = RegisterUserForm()

    return render(request, 'authenticate/register_user.html', {'form': form})

    
