from django.urls import path

from src import views

urlpatterns = [
    path('get_one_src_info/', views.get_one_src_info),
    path('get_one_src_page_data/', views.get_one_src_page_data),
    path('get_one_src_page_count/', views.get_one_src_page_count),
    path('get_front_src_info/', views.get_front_src_info),
    path('add_one_src/', views.add_one_src),
    path('add_two_src/', views.add_two_src),
    path('get_two_src_info/', views.get_two_src_info),
    path('add_four_src/', views.add_four_src),
    path('update_four_src/', views.update_four_src),
    path('get_four_src_info/', views.get_four_src_info),
    path('update_one_src/', views.update_one_src),
    path('get_to_name_one_src/', views.get_to_name_one_src),
    path('get_two_src_page_count/', views.get_two_src_page_count),
    path('get_two_src_page_data/', views.get_two_src_page_data),
    path('update_two_src/', views.update_two_src),
    path('query_two_src/', views.query_two_src),
    path('query_four_src/', views.query_four_src),
    path('get_four_src_page_data/', views.get_four_src_page_data),
    path('get_four_src_page_count/', views.get_four_src_page_count),
]
