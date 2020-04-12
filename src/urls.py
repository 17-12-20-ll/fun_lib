from django.urls import path

from src import views

urlpatterns = [
    # one
    path('get_one_src_info/', views.get_one_src_info),
    path('add_one_src/', views.add_one_src),
    path('update_one_src/', views.update_one_src),
    path('get_to_name_one_src/', views.get_to_name_one_src),
    # ================
    path('get_one_src/', views.get_one_src),

    # two
    path('add_two_src/', views.add_two_src),
    path('get_two_src_info/', views.get_two_src_info),
    path('get_two_src_page_count/', views.get_two_src_page_count),
    path('get_two_src_page_data/', views.get_two_src_page_data),
    path('update_two_src/', views.update_two_src),
    path('update_two_src/', views.update_two_src),
    # ============
    path('get_two_src/', views.get_two_src),
    # three
    path('add_three_src/', views.add_three_src),
    path('update_three_src/', views.update_three_src),
    path('get_three_src_info/', views.get_three_src_info),
    path('get_three_src_page_data/', views.get_three_src_page_data),
    path('get_three_src_page_count/', views.get_three_src_page_count),
    # ================= get_three_src
    path('get_three_src/', views.get_three_src),
    # four
    path('get_four_src/', views.get_four_src),
    # four
    path('add_four_src/', views.add_four_src),
    path('update_four_src/', views.update_four_src),
    path('get_four_src_info/', views.get_four_src_info),
    path('query_four_src/', views.query_four_src),
    # other
    path('get_front_src_info/', views.get_front_src_info),
    path('test/', views.test),
    path('del_data/', views.del_data),
    # 获取资源
    path('get_resource/', views.get_resource),
    # 资源检测错误回调接口
    path('re_email/', views.re_email),
]
