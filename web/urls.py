from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Signin.as_view(), name='login'),
    path('logout/', views.Signout.as_view(), name='logout'),
    path('job-upload/', views.JobUpload.as_view(), name='job-upload'),
    path('job-history/', views.JobHistory.as_view(), name='job-history'),
    path('atmel/', views.get_jobs, name='get-jobs'),
    path('atmega/', views.upload_jobs, name='upload-jobs'),
    path('tony/', views.token, name='token'),
    path('deploy/', views.deploy, name='deploy'),
]