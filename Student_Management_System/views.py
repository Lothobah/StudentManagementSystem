from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect,HttpResponse
from Student_Management_System.EmailBackEnd import EmailBackEnd
from django.contrib import messages
from django.urls import reverse
# Create your views here.

def ShowDemoPage(request):
    return render(request, "demo.html")

def ShowLoginPage(request):
    return render(request, "login_page.html")

def DoLogin(request):
    if request.method!="POST":
            return HttpResponse("<h3>method not allowed<h3/>")
    else:
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect("/admin_homepage")
            elif user.user_type=="2":
                return HttpResponseRedirect(reverse("staff_homepage"))
            else:
                return HttpResponseRedirect(reverse("student_homepage"))
        else:
            messages.error(request,'Invalid Login Details')
            return HttpResponseRedirect("/")


def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User :"+request.user.email+"UserType :"+ request.user.user_type)
    else:
        messages.error(request,'Invalid Login Details')
        return HttpResponse("Please login first")

def Logout_User(request):
    logout(request)
    return HttpResponseRedirect("/")
        