from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('progress/', views.my_progress, name='my_progress'),
    path('profile/', views.my_profile, name='my_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('tutor/', include('tutor.urls')),
    path('courses/', include('courses.urls')),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-dashboard/student/<int:user_id>/', views.student_detail, name='student_detail'),
]