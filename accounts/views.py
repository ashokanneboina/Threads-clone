from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser
from .forms import LoginForm, SignupForm
from django.contrib.auth.decorators import login_required
# Create your views here.
def home_view(request):
    user = request.user
    return render(request, 'home.html',{'user': user})
def login_view(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
        
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                return render(request,"login.html")
    return render(request,"login.html",{"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
    
def signup_view(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            
            login(request,user)
            return redirect('home')
    return render(request,"signup.html",{"form": form})