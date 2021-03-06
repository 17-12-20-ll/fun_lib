from django.urls import path

from operation import views

urlpatterns = [
    path('add_help_class/', views.add_help_class),
    path('update_help_class/', views.update_help_class),
    path('get_help_class_info/', views.get_help_class_info),
    path('add_help_list/', views.add_help_list),
    path('update_help_list/', views.update_help_list),
    path('get_help_list_info/', views.get_help_list_info),
    path('get_admin_log_data/', views.get_admin_log_data),
    path('get_admin_log_count/', views.get_admin_log_count),
    path('get_order/', views.get_order),
]
