from django.shortcuts import render

# Create your views here.
def home(reqeust):
    return  render(reqeust ,'main/home.html')
