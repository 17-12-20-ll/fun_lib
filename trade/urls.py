from django.urls import path

from trade import views

urlpatterns = [
    path('get_trade_type_info/', views.get_trade_type_info),
    # 返回支付二维码
    path('get_pay_qr_code/', views.get_pay_qr_code),
    path('get_order_status/', views.get_order_status),
    path('invoice/', views.invoice),
    path('add_card/', views.add_card),
    path('add_n_card/', views.add_n_card),
    path('get_card_info/', views.get_card_info),
    path('update_trade_type/', views.update_trade_type),
    path('query_trade_type/', views.query_trade_type),
    path('add_trade_type/', views.add_trade_type),
    path('get_card_page_data/', views.get_card_page_data),
    path('get_card_page_count/', views.get_card_page_count),
    path('alipay_return/', views.alipay_return),
    path('card_recharge/', views.card_recharge),
]
