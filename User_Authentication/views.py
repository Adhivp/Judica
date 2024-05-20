from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from User_Authentication.models import *

def register(request):
    messages_list = [] 
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_profile = UserProfile.objects.create(user=user)
                user_profile.save()

                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')

    for message in messages.get_messages(request):
        messages_list.append(message)
    context = {'messages': messages_list}
    return render(request, 'register.html', context)

def user_login(request):
    messages_list = []
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('register')
        else:
            messages.error(request, 'Invalid username or password.')
    for message in messages.get_messages(request):
        messages_list.append(message)
    context = {'messages': messages_list}
    return render(request, 'login.html', context)
