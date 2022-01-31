from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from web.forms import SignUpForm, FileUploadForm


def index(request):
    return render(request, 'index.html')


class Signup(View):
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=username, password=raw_password)
            login(request, user)
            return redirect('/')

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
class RenderUpload(View):
    form_class = FileUploadForm
    template_name = "render-upload.html"

    def get(self, request):
        form = self.form_class()
        return render(request, 'render-upload.html', {'form': form})
