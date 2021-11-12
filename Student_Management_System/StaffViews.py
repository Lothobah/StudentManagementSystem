from django.shortcuts import render
from Student_Management_System.models import Subjects,SessionYearModel,Students,AdminHOD,Attendance,AttendanceReport,Staffs,StaffLeaveReport
from Student_Management_System.models import StaffFeedback,CustomUser,Staffs,Courses,StudentResults
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.core import serializers
from django.contrib import messages
import json
from django.urls import reverse

def staff_homepage(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    course_id_list=[]
    for subject in subjects:
        course=Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    final_course=[]
    #removes duplicate course ID.
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count=Students.objects.filter(course_id__in=final_course).count()
    #fetch all Attendance Counts
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()
    #fetch all approved Leave
    staff=Staffs.objects.get(admin=request.user.id)
    leave_count=StaffLeaveReport.objects.filter(staff_id=staff.id,leave_status=1).count()
    subject_count=subjects.count()
    #fetch attendance data by subject
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)
    students_attendance=Students.objects.filter(course_id__in=final_course)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)
    return render(request,"staff_template/staff_homepage.html",{"students_count":students_count,"attendance_count":attendance_count,"leave_count":leave_count,"subject_count":subject_count,"subject_list":subject_list,"attendance_list":attendance_list,"student_list":student_list,"student_list_attendance_present":student_list_attendance_present,"student_list_attendance_absent":student_list_attendance_absent})

def staff_take_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"staff_template/staff_take_attendance.html",{"subjects":subjects,"session_years":session_years})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_year_model=SessionYearModel.objects.get(id=session_year)
    students=Students.objects.filter(course_id=subject.course_id,session_year_id=session_year_model)
    student_data=serializers.serialize("python", students)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.last_name+" "+student.admin.first_name}
        list_data.append(data_small)
    return JsonResponse(list_data,content_type="application/json",safe=False)
@csrf_exempt #it is added so you don't need to add csrf Token for saving data using Ajax
def save_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    subject_id=request.POST.get("subject_id")
    attendance_date=request.POST.get("attendance_date")
    session_year_id=request.POST.get("session_year_id")
    subject_model=Subjects.objects.get(id=subject_id)
    session_year_model=SessionYearModel.objects.get(id=session_year_id)
    json_student=json.loads(student_ids)
    #print(data[0]["id"])
    try:
        attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_year_model)
        attendance.save()

        for stud in json_student:
            student=Students.objects.get(admin=stud["id"])
            attendance_report=AttendanceReport(student_id=student,attendance_id=attendance,status=stud["status"])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")

def staff_update_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request, "staff_template/staff_update_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})
@csrf_exempt
def get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    subject_obj=Subjects.objects.get(id=subject)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":attendance_single.attendance_date,"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)
    return JsonResponse(attendance_obj, safe=False)
@csrf_exempt
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")

    attendance=Attendance.objects.get(id=attendance_date)
    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.last_name+" "+student.student_id.admin.first_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(list_data,content_type="application/json",safe=False)
@csrf_exempt
def save_update_attendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)
    json_student=json.loads(student_ids)
    try:

        for stud in json_student:
            student=Students.objects.get(admin=stud["id"])
            attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
            attendance_report.status=stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERROR")

def staff_apply_leave(request):
    staff_obj=Staffs.objects.get(admin=request.user.id)
    leave_data=StaffLeaveReport.objects.filter(staff_id=staff_obj)
    return render(request, "staff_template/staff_apply_leave.html",{"leave_data":leave_data})

def staff_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_reason=request.POST.get("leave_reason")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            leave_report=StaffLeaveReport(staff_id=staff_obj,leave_date=leave_date,leave_message=leave_reason,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied For Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        except:
            messages.error(request,"Failed To Apply For Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
def staff_feedback(request):
    staff_id=Staffs.objects.get(admin=request.user.id)
    feedback_data=StaffFeedback.objects.filter(staff_id=staff_id)
    return render(request, "staff_template/staff_feedback.html",{"feedback_data":feedback_data})
def staff_feedback_save(request):
        if request.method!="POST":
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        else:
            feedback_msg=request.POST.get("feedback_msg")

            staff_obj=Staffs.objects.get(admin=request.user.id)
            try:
                feedback=StaffFeedback(staff_id=staff_obj,feedback=feedback_msg,feedback_reply="")
                feedback.save()
                messages.success(request, "Successfully Sent Feedback")
                return HttpResponseRedirect(reverse("staff_feedback"))
            except:
                messages.error(request,"Failed To Apply For Leave")
                return HttpResponseRedirect(reverse("staff_feedback"))
def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    return render(request, "staff_template/staff_profile.html",{"user":user,"staff":staff})
def edit_staff_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_profile"))
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
            staff=Staffs.objects.get(admin=custom_user.id)
            staff.address=address
            staff.save()
            messages.success(request, "Successfully Edited Staff Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request, "Failed to Edit Staff Profile")
            return HttpResponseRedirect(reverse("staff_profile")) 
        
def staff_add_result(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    assignment_mark=request.POST.get("assignment_mark")
    exam_mark=request.POST.get("exam_mark")
    #total_mark=assignment_mark+exam_mark
    
    return render(request, "staff_template/staff_add_result.html",{"subjects":subjects,"session_years":session_years})

def save_student_result(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_add_result"))
        
    student_admin_id=request.POST.get("student_list")
    assignment_mark=float(request.POST.get('assignment_mark'))
    assignment_mark=(assignment_mark / 100) * 30
    exam_mark=float(request.POST.get('exam_mark'))
    #converts row exam mark out of 100 to 70%
    exam_mark=(exam_mark / 100) * 70
    total_mark=assignment_mark + exam_mark
    subject_id=request.POST.get("subject")
    student_obj=Students.objects.get(admin=student_admin_id)
    subject_obj=Subjects.objects.get(id=subject_id)
    
    #try:
    #check_list=StudentResults.objects.filter(student_id=student_obj,subject_id=subject_obj).exists()
    #if check_list:
        #assignment_mark=float(request.POST.get('assignment_mark'))
        #exam_mark=float(request.POST.get('exam_mark'))
        #total_mark=assignment_mark + exam_mark
        #result=StudentResults.objects.get(student_id=student_obj,subject_id=subject_obj)
    """ result.exam_mark=exam_mark
        result.assignment_mark=assignment_mark
        total_mark=assignment_mark + exam_mark
        result.total_mark=assignment_mark + exam_mark"""
        #result.save()
        
        #messages.success(request, "successfully updated Student Results")
        #return HttpResponseRedirect(reverse("staff_add_result"))
    #else:
        
    result=StudentResults(student_id=student_obj,subject_id=subject_obj,assignment_mark=assignment_mark,exam_mark=exam_mark,total_mark=total_mark)
    result.save()
    messages.success(request,"Successfully Added Results")
    return HttpResponseRedirect(reverse("staff_add_result"))
    #except:
        #messages.error(request, "Failed To Add Result")
        #return HttpResponseRedirect(reverse("staff_add_result"))
    
@csrf_exempt
def fetch_student_results(request):
    subject_id=request.POST.get("subject_id")
    student_id=request.POST.get("student_id")
    student_obj=Students.objects.get(admin=student_id)
    result=StudentResults.objects.filter(student_id=student_obj.id,subject_id=subject_id).exists() 
    if result:
        result=StudentResults.objects.get(student_id=student_obj.id,subject_id=subject_id)
        result_data={"exam_mark":result.exam_mark,"assignment_mark":result.assignment_mark}
        print(result_data)
        return HttpResponse(json.dumps(result_data))
    else:
        return HttpResponse("False")   
    

#add two numbers
def add_two_numbers(request):
    if "number1" in request.POST:
        val1=float(request.POST.get("number1"))
    else:
        val1=False
    if "number2" in request.POST:
        val2=float(request.POST.get("number2"))
    else:
        val2=False
    res=val1 + val2
    #return render(request,"staff_template/add_two_numbers.html")
    return render(request, "staff_template/add_two_numbers.html",{"result":res})