from django.urls import path

from src import views

urlpatterns = [
    path('get_one_src_info/', views.get_one_src_info),
    path('get_front_src_info/', views.get_front_src_info),
    path('add_one_src/', views.add_one_src),
    path('add_two_src/', views.add_two_src),
    path('get_two_src_info/', views.get_two_src_info),
    path('insert/', views.insert),
    path('add_four_src/', views.add_four_src),
    path('get_four_src_info/', views.get_four_src_info),
]
