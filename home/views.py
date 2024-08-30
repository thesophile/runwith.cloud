from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request,'hello.html',{'name':'Abhinav'}) 
 
def donate(request):
    return render(request, 'donate.html')