import datetime
import os
from logging import log

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Value, Count, Q, CharField
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.contrib.auth.decorators import user_passes_test

from mupparimanam.settings import BASE_DIR
from web.forms import SignUpForm, FileUploadForm, CustomAuthForm
from web.models import JobsHistory, JobFiles, Files

from uuid import UUID

User = get_user_model()


def superuser_required():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_superuser

        return WrappedClass

    return wrapper


def index(request):
    return render(request, 'index.html')


class Signup(View):
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'signup.html', {'form': form})

    def get(self, request):
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


class Signin(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            next_page = request.GET['next']
            login(request, user)
            return redirect(next_page)
        else:
            form = CustomAuthForm()
            messages.error(request, 'Email Id / Password did not match.')
            return render(request, 'login.html', {'form': form})

    def get(self, request):
        form = CustomAuthForm()
        return render(request, 'login.html', {'form': form})


class Signout(View):
    def get(self, request):
        logout(request)
        return redirect("/")


@method_decorator(login_required, name='dispatch')
class JobUpload(View):
    form_class = FileUploadForm
    template_name = "render-upload.html"
    success_template_name = "render-upload.html"

    def get(self, request):
        jobs = JobsHistory.objects.filter(user=request.user, remove_status=Value(0)).count()
        if jobs > 4:
            messages.error(request, 'Quota exhausted, please clear some files before upload new picture.')
            return redirect("job-history")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form_id = form.save()
            job = JobsHistory.objects.create(user=request.user)
            files = JobFiles.objects.create(job=job, files=form_id)
            return redirect("job-history")
        else:
            for err in form.errors:
                messages.error(request, form.errors[err])
            return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class JobHistory(View):
    template_name = "job-history.html"

    def get(self, request):
        user = request.user
        job_list = JobsHistory.objects.filter(user=user, remove_status=Value(0)).values(
            'job_id', 'jobfiles__files__file', 'complete_status', 'obj_file', 'remove_status') \
            .order_by('-initiated_on')
        return render(request, self.template_name, {'list': job_list})

    def post(self, request):
        job_id = request.POST["job-id"]
        file = Files.objects.get(jobfiles__job_id=job_id)
        if file.file.name != '':
            delete_file(file.file.url)
        file.delete()
        job = JobsHistory.objects.get(user=request.user, job_id=job_id)
        if job.obj_file.name != '':
            delete_file(job.obj_file.url)
        job.delete()
        return redirect("job-history")


@method_decorator(login_required, name='dispatch')
@superuser_required()
class AdminPage(View):
    template_name = "admin-page.html"

    def get(self, request):
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if is_ajax:
            column = ['id', 'email', 'date_joined', 'count']
            start = int(request.GET['start'])
            length = int(request.GET['length'])
            column_id = int(request.GET['order[0][column]'][0])
            order_dir = request.GET['order[0][dir]']
            order_by = column[column_id]
            draw = int(request.GET['draw'])
            if column_id == 0 and order_dir == 'asc':
                order_by = '-' + order_by
            elif order_dir == 'desc':
                if column_id > 0:
                    order_by = '-' + order_by
            if start > 0:
                length += start
            user_list = User.objects.exclude(id=Value(1)).values(
                'id', 'email', 'date_joined').annotate(
                count=Count('jobshistory__job_id'),
                pending=Count('jobshistory__job_id', filter=Q(jobshistory__complete_status=Value(0))),
                inprogress=Count('jobshistory__job_id', filter=Q(jobshistory__complete_status=Value(1))),
                completed=Count('jobshistory__job_id', filter=Q(jobshistory__complete_status=Value(2))),
                failed=Count('jobshistory__job_id', filter=Q(jobshistory__complete_status=Value(3))),
                jobs=Concat('pending', Value(", "), 'inprogress', Value(", "), 'completed', Value(", "), 'failed',
                            output_field=CharField())
            ).order_by(order_by)[start:length]
            user_list = list(user_list)
            records_total = User.objects.exclude(id=Value(1)).all().count()
            # if draw == 1:
            records_filtered = records_total
            # else:
            #     records_filtered = len(user_list)
            result = {
                'data': user_list,
                'draw': draw,
                'recordsTotal': records_total,
                'recordsFiltered': records_filtered
            }
            return JsonResponse(result, safe=False)
        else:
            jobs = JobsHistory.objects.exclude(user_id=Value(1)).aggregate(
                Pending=Count('job_id', filter=Q(complete_status=Value(0))),
                Completed=Count('job_id', filter=Q(complete_status=Value(2))),
                Failed=Count('job_id', filter=Q(complete_status=Value(3))),
            )
            user_count = User.objects.exclude(id=Value(1)).all().count()
            return render(request, self.template_name, {'jobs': jobs, 'users': user_count})
            # return render(request, self.template_name)

    def post(self, request):
        job_id = request.POST["job-id"]
        file = Files.objects.get(jobfiles__job_id=job_id)
        if file.file.name != '':
            delete_file(file.file.url)
        file.delete()
        job = JobsHistory.objects.get(user=request.user, job_id=job_id)
        # job.remove_status = 1
        if job.obj_file.name != '':
            delete_file(job.obj_file.url)
        job.delete()
        return redirect("job-history")


def get_jobs(request):
    if request.method == 'GET':
        key = request.GET['k']
        if key == 'ardu':
            JobsHistory.objects.filter(remove_status=Value(0), complete_status=Value(1)).update(
                complete_status=Value(3)
            )
            job_list = JobsHistory.objects.filter(remove_status=Value(0), complete_status=Value(0)).values(
                'job_id', 'jobfiles__files__file'
            ).order_by('initiated_on')[:1]
            result = list(job_list)
            if len(result):
                JobsHistory.objects.filter(job_id=job_list[0]['job_id']).update(complete_status=Value(1))
            return JsonResponse(result, safe=False)
        else:
            return HttpResponse("No")
    else:
        return HttpResponse("Fuck you")


@csrf_exempt
def upload_jobs(request):
    if request.method == 'POST':
        key = request.POST['k']
        if key == 'ardu':
            files = request.FILES
            for name in files:
                file = File(files[name], name=name)
                job_id = name.replace(".obj", "")
                job_id = UUID(job_id)
                job = JobsHistory.objects.get(job_id=job_id)
                job.obj_file = file
                job.complete_status = Value(2)
                job.completed_on = datetime.datetime.now()
                job.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("No")
    else:
        return HttpResponse("Fuck you")


def token(request):
    if request.method == 'GET':
        key = request.GET['k']
        if key == 'ardu':
            return render(request, 'token.html')
    return HttpResponse("Fuck you")


def delete_file(path):
    file_path = os.path.join(str(BASE_DIR) + path)
    if os.path.isfile(file_path):
        os.remove(file_path)


def deploy(request):
    if request.method == 'GET':
        try:
            os.system('sudo git pull')
            os.system('sudo systemctl restart mupparimanam.service')
            return HttpResponse("Success")
        except Exception as e:
            print(e)
            return HttpResponse("Failed")
