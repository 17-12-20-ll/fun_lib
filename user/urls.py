from django.urls import path

from user import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('update_profile/', views.update_profile),
    path('update/', views.update),
    path('update_pwd/', views.update_pwd),
    path('forget_email_pwd/', views.forget_email_pwd),
    path('update_forget_email_pwd/', views.update_forget_email_pwd),
    path('get_user_info/', views.get_user_info),
    path('add_group/', views.add_group),
    path('del_group/', views.del_group),
    path('update_group/', views.update_group),
    path('get_group_info/', views.get_group_info),
    path('get_to_name_info/', views.get_to_name_info),
    path('captcha/', views.captcha),
    path('get_token_info/', views.get_token_info),
    path('check_img_code/', views.check_img_code),
    path('check_token_result/', views.check_token_result),
    path('get_admins/', views.get_admins),
    path('update_admin/', views.update_admin),
    path('add_admin/', views.add_admin),
    path('query_admin/', views.query_admin),
    path('get_users/', views.get_users),
    path('get_user_count/', views.get_user_count),
    path('add_back_user/', views.add_back_user),
    path('query_user/', views.query_user),
    path('check_user/', views.check_user),
    path('to_group_one_src/', views.to_group_one_src),
    # 新分页接口
    path('get_user/', views.get_user),
]
