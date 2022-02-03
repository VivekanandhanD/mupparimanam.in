from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import AuthenticationForm
from django.db.models import CharField, DateField, Func, F, Value
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from web.forms import SignUpForm, FileUploadForm, CustomAuthForm
from web.models import JobsHistory, JobFiles


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
            'job_id', 'initiated_on', 'jobfiles__files__file', 'complete_status', 'obj_file', 'remove_status')\
            .order_by('-initiated_on')
        return render(request, self.template_name, {'list': job_list})

    def post(self, request):
        job_id = request.POST["job-id"]
        job = JobsHistory.objects.get(user=request.user, job_id=job_id)
        job.remove_status = 1
        job.save()
        return redirect("job-history")


def get_jobs(request):
    if request.method == 'GET':
        key = request.GET['k']
        if key == 'ardu':
            job_list = JobsHistory.objects.filter(remove_status=Value(0), complete_status=Value(0)).values(
                'job_id', 'jobfiles__files__file'
            )
            result = list(job_list)
            # job_list.update(complete_status=Value(1))
            return JsonResponse(result, safe=False)
        else:
            return HttpResponse("No")
    else:
        return HttpResponse("Fuck you")
