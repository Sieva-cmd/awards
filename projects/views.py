from django.shortcuts import render
import datetime as dt
from django.contrib.auth.decorators import login_required
from .models import Post,Profile,Rating
from django.http  import Http404,HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import  render, redirect,get_object_or_404
from .forms import NewUserForm,PostForm,RatingForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

import random
from django.contrib.auth.decorators import login_required
from django.urls import reverse

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

