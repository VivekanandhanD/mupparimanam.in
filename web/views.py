from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from web.forms import SignUpForm, FileUploadForm
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
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form})

    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})


class Signout(View):
    def get(self, request):
        logout(request)
        return redirect("/")


@method_decorator(login_required, name='dispatch')
class JobUpload(View):
    form_class = FileUploadForm
    template_name = "render-upload.html"

    def get(self, request):
        form = self.form_class()
        return render(request, 'render-upload.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            # form = form.save()
            form_id = form.save()
            job = JobsHistory.objects.create(user=request.user)
            files = JobFiles.objects.create(job=job, files=form_id)
        return render(request, 'render-upload.html', {'form': form})
