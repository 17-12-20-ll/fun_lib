from django.urls import path

from operation import views

urlpatterns = [
    path('add_help_class/', views.add_help_class),
    path('update_help_class/', views.update_help_class),
    path('get_help_class_info/', views.get_help_class_info),
    path('add_help_list/', views.add_help_list),
    path('update_help_list/', views.update_help_list),
    path('get_help_list_info/', views.get_help_list_info),
    ]