# use to protect each category of users from accessing others homepage
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect,HttpResponse


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename=view_func.__module__
        print(modulename)
        user=request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "Student_Management_System.HodViews":
                    pass
                elif modulename == "Student_Management_System.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_homepage"))
            elif user.user_type == "2":
                if modulename == "Student_Management_System.StaffViews" or modulename == "Student_Management_System.EditResultViewClass":
                    pass
                elif modulename == "Student_Management_System.views" or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse("staff_homepage"))
            elif user.user_type == "3":
                if modulename == "Student_Management_System.StudentViews" or modulename == "django.views.static":
                    pass
                elif modulename == "Student_Management_System.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_homepage"))
            else:
                return HttpResponseRedirect(reverse("show_login"))
        else:
            if request.path == reverse("show_login") or request.path == reverse("do_login") or modulename == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))