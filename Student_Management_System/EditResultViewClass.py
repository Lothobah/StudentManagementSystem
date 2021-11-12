from django.shortcuts import render
from django.views import View
from Student_Management_System.forms import EditResultForm
from  Student_Management_System.models import Students,Subjects,StudentResults
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
class EditResultViewClass(View):
    def get(self,request,*args,**kwargs):
        staff_id=request.user.id
        edit_result_form=EditResultForm(staff_id=staff_id)
        return render(request, "staff_template/staff_edit_result.html",{"form":edit_result_form})

    def post(self,request,*args,**kwargs):
        form=EditResultForm(request.POST,staff_id=request.user.id)
        if form.is_valid():
            student_admin_id=form.cleaned_data['student_id']
            assignment_mark=float(form.cleaned_data['assignment_mark'])
            exam_mark=float(form.cleaned_data['exam_mark'])
            total_mark=assignment_mark + exam_mark
            subject_id=form.cleaned_data['subject_id']
            student_obj=Students.objects.get(admin=student_admin_id)
            subject_obj=Subjects.objects.get(id=subject_id)
            result=StudentResults.objects.get(student_id=student_obj,subject_id=subject_obj)
            result.exam_mark=exam_mark
            result.assignment_mark=assignment_mark
            result.total_mark=total_mark
            result.save()
            messages.success(request,"Successfully Updated Results")
            return HttpResponseRedirect(reverse("edit_student_result"))
        else:
            form=EditResultForm(request.POST,staff_id=request.user.id)
            messages.error(request,"Failed to Update Results")
            return render(request, "staff_template/staff_edit_result.html",{"form":form})
