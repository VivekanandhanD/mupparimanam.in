from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Signin.as_view(), name='login'),
    path('logout/', views.Signout.as_view(), name='logout'),
    path('render-upload/', views.RenderUpload.as_view(), name='renderupload')
]