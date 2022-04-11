from django.shortcuts import render
import datetime as dt
from django.contrib.auth.decorators import login_required
from .models import Post,Profile,Rating
from django.http  import Http404,HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import  render, redirect,get_object_or_404
from .forms import NewUserForm,PostForm,RatingForm,UpdateUserForm,UpdateUserProfileForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

import random
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import  Post,Profile
from .serializer import Postserializer,ProfileSerializer
from rest_framework import status

# Create your views here.

def home(request):
    current_user = request.user
    if request.method == "POST":
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse("home"))
    else:
        form = PostForm()
    
    try:
        posts = Post.objects.all()
        posts = posts[::-1]
        post_index = random.randint(0, len(posts)-1)
        random_post = posts[post_index]
        print(random_post.photo)
    except Post.DoesNotExist:
        posts = None
    return render(request, 'main/home.html',{'form':form,'current_user':current_user,'random_post': random_post,'posts':posts})
def postProject(request):
    current_user = request.user
    if request.method == "POST":
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
        return redirect('home')
    else:
        form = PostForm()

    return render(request,'main/post.html',{'form':form,'current_user':current_user})    

@login_required(login_url='login')
def project(request, post):
    post = Post.objects.get(title=post)
    ratings = Rating.objects.filter(user=request.user, post=post).first()
    rating_status = None
    current_user=request.user
    

    if request.method == "POST":
        post_form = PostForm(request.POST,request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse("home"))
    else:
        post_form = PostForm()
    
    if ratings is None:
        rating_status = False
    else:
        rating_status = True
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rate_result = form.save(commit=False)
            rate_result.user = request.user
            rate_result.post = post
            rate_result.save()
            post_ratings = Rating.objects.filter(post=post)

            design_rate = [d.design for d in post_ratings]
            design_av = sum(design_rate) / len(design_rate)

            usability_rate = [us.usability for us in post_ratings]
            usability_av = sum(usability_rate) / len(usability_rate)

            content_rate = [content.content for content in post_ratings]
            content_av = sum(content_rate) / len(content_rate)

            score = (design_av + usability_av + content_av) / 3
            print(score)
            rate_result.design_average = round(design_av, 2)
            rate_result.usability_average = round(usability_av, 2)
            rate_result.content_average = round(content_av, 2)
            rate_result.score = round(score, 2)
            rate_result.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = RatingForm()
    return render(request, 'main/project.html', {'post': post,'rating_form': form,'rating_status': rating_status,'current_user':current_user,'post_form':post_form})



def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
		
			messages.success(request, "Registration successful." )
			return redirect(login_request)
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="main/register.html", context={"register_form":form})


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username,password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect(home)
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request,template_name="main/login.html", context={"login_form":form})


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect(login_request)    

def search_results(request):
    if 'post' in request.GET and request.GET["post"]:
        search_term =request.GET.get("post")
        searched_post =Post.search_project(search_term)
        message =f"{search_term}"

        return render(request,'main/search.html',{"message":message,"posts":searched_post})
    else:
        message ="You haven't searched for an image"
        return render(request, 'main/search.html', {"message":message})    


@login_required(login_url='login')
def user_profile(request, username):
    current_user=request.user
    
    if request.method == "POST":
        post_form = PostForm(request.POST,request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse("home"))
    else:
        post_form = PostForm()
        
    user_poster = get_object_or_404(User, username=username)
    if request.user == user_poster:
        return redirect('profile', username=request.user.username)
    user_posts = user_poster.posts.all()
    
    
    return render(request, 'main/poster.html', {'user_poster': user_poster,'user_posts':user_posts,'post_form':post_form,'current_user':current_user})

@login_required(login_url='login')
def profile(request, username):
    posts = request.user.posts.all()
    current_user=request.user
    
    if request.method == "POST":
        post_form = PostForm(request.POST,request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse("home"))
    else:
        post_form = PostForm()
        
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateUserProfileForm(instance=request.user.profile)

    return render(request, 'main/profile.html', {'user_form':user_form,'profile_form':profile_form,'posts':posts,'post_form':post_form})


class projectList(APIView):
    def get(self,request,format=None):
        all_projects =Post.objects.all()
        serializers =Postserializer(all_projects, many=True)
        return Response(serializers.data)

    def post(self, request, format=None):
        serializers = Postserializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)    


class profileList(APIView):
    def get(self,request,format=None):
        all_profiles =Profile.objects.all()
        serializers =ProfileSerializer(all_profiles, many=True)
        return Response(serializers.data)

    def post(self, request, format=None):
        serializers = ProfileSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)    
    