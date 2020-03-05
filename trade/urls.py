from django.urls import path

from trade import views

urlpatterns = [
    path('get_trade_type_info/', views.get_trade_type_info),
    # 返回支付二维码
    path('get_pay_qr_code/', views.get_pay_qr_code),
    path('add_card/', views.add_card),
    path('add_n_card/', views.add_n_card),
    path('get_card_info/', views.get_card_info),
]
