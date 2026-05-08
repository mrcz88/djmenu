from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib import messages
from .forms import RegisterForm

# Create your views here.

def register_base(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # aggiunge un messaggio a messages. Ci vuole uno spazio apposito per mostrarli in menu:index
            messages.success(request, f'Welcome {username}, your account has been created.')
            return redirect('menu:index')
    form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # aggiunge un messaggio a messages. Ci vuole uno spazio apposito per mostrarli in menu:index
            messages.success(request, f'Welcome {username}, your account has been created.')
            return redirect('users:login')
    form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('menu:index')

def profile(request):
    return render(request, 'users/profile.html')