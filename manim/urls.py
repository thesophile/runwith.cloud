from django.urls import path

from . import views

urlpatterns = [
    path("", views.execute_code, name='manim_home'),
    path('get-code/<int:code_id>/', views.get_code, name='get_code'),
    path('save_code/', views.save_code, name='save_code'),
]