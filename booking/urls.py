from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_booking, name='student_booking'),
    path('book/', views.book_appointment, name='book'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/action/<int:appointment_id>/<str:action>/', views.appointment_action, name='appointment_action'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('slots/', views.available_slots, name='available_slots'),
]