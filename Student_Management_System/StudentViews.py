from django.shortcuts import render
from Student_Management_System.models import Students,Courses,Subjects,CustomUser
from Student_Management_System.models import Attendance,AttendanceReport,StudentFeedback
from Student_Management_System.models import StudentLeaveReport,StudentResults
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import datetime
def student_homepage(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()
    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request, "student_template/student_homepage.html",{"attendance_total":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent})

def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request, "student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")
    start_date_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_obj=CustomUser.objects.get(id=request.user.id)
    student_obj=Students.objects.get(admin=user_obj)
    attendance=Attendance.objects.filter(attendance_date__range=(start_date_parse,end_date_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=student_obj)

    return render(request, "student_template/student_attendance_data.html",{"attendance_reports":attendance_reports})

def student_apply_leave(request):
    student_obj=Students.objects.get(admin=request.user.id)
    leave_data=StudentLeaveReport.objects.filter(student_id=student_obj)
    return render(request, "student_template/student_apply_leave.html",{"leave_data":leave_data})

def student_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_reason=request.POST.get("leave_reason")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=StudentLeaveReport(student_id=student_obj,leave_date=leave_date,leave_message=leave_reason,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied For Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))
        except:
            messages.error(request,"Failed To Apply For Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))
def student_feedback(request):
    student_obj=Students.objects.get(admin=request.user.id)
    feedback_data=StudentFeedback.objects.filter(student_id=student_obj)
    return render(request, "student_template/student_feedback.html",{"feedback_data":feedback_data})
def student_feedback_save(request):
        if request.method!="POST":
            return HttpResponseRedirect(reverse("student_apply_leave"))
        else:
            feedback_msg=request.POST.get("feedback_msg")

            student_obj=Students.objects.get(admin=request.user.id)
            try:
                feedback=StudentFeedback(student_id=student_obj,feedback=feedback_msg,feedback_reply="")
                feedback.save()
                messages.success(request, "Successfully Sent Feedback")
                return HttpResponseRedirect(reverse("student_feedback"))
            except:
                messages.error(request,"Failed To Apply For Leave")
                return HttpResponseRedirect(reverse("student_feedback"))

def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request, "student_template/student_profile.html",{"user":user,"student":student})
def edit_student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            custom_user=CustomUser.objects.get(id=request.user.id)
            custom_user.first_name=first_name
            custom_user.last_name=last_name
            if password!=None and password!="":
                custom_user.set_password(password)
            custom_user.save()
            student=Students.objects.get(admin=custom_user.id)
            student.address=address
            student.save()
            messages.success(request, "Successfully Edited Student Profile")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Edit Student Profile")
            return HttpResponseRedirect(reverse("student_profile")) 
        
def student_view_results(request):
    student=Students.objects.get(admin=request.user.id)
    student_result=StudentResults.objects.filter(student_id=student.id)
    return render(request,"student_template/student_view_results.html",{"student_result":student_result})
    