from django.urls import path

from trade import views

urlpatterns = [
    path('get_trade_type_info/', views.get_trade_type_info),
    # 返回支付二维码
    path('get_pay_qr_code/', views.get_pay_qr_code),
]
