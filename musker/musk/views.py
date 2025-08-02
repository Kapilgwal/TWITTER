from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Profile,Meep
from .forms import MeepForm,SignUpForm,UserUpdateForm,ProfilePicForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django import forms 
from django.contrib.auth.models import User

def home(request):

    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request,("Your meep has been posted"))
                return redirect('home')
        
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps" : meeps, "form" : form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps" : meeps})
  

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user = request.user)
        return render(request, 'profile_list.html', {"profiles" : profiles})
    
    else:
        messages.success(request,("You must be logged in the application"))
        return redirect('home')
    
def profile(request,pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id = pk)
        meeps = Meep.objects.filter(id = pk).order_by("-created_at")
        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']

            if action == "unfollow":
                current_user_profile.follows.remove(profile)

            elif action == "follow":
                current_user_profile.follows.add(profile)

            current_user_profile.save()

        return render(request,'profile.html',{"profile" : profile, "meeps" : meeps})
    
    else:
        messages.success(request,("You must be logged in the application"))
        return redirect('home')
    
def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,username = username,password = password)

        if user is not None:
            login(request,user)
            messages.success(request,("You have been logged in"))
            return redirect('home')
        
        else:
            messages.error(request,("Your username or password is invalid"))
            return redirect('login')

    else:
        return render(request,'login.html')

def logout_user(request):
    logout(request)
    messages.success(request,"You have been logged out")
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']

            user = authenticate(request,username = username,password = password)
            login(request,user)
            messages.success(request,'You have been successfully registered')
            return redirect('home')
            
    return render(request,'register.html',{'form' : form})

from .forms import UserUpdateForm
from django.shortcuts import get_object_or_404

def update_user(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect('home')

    user = request.user
    profile_user = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = ProfilePicForm(request.POST, request.FILES, instance=profile_user)
        print(request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            print("Uploaded image file:", profile.profile_image)
            profile.save()

            messages.success(request, "Your profile has been updated.")
            login(request, user)  
            return redirect('home')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfilePicForm(instance=profile_user)

    return render(request, 'update_user.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })