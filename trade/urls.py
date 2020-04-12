from django.urls import path

from trade import views

urlpatterns = [
    path('get_trade_type_info/', views.get_trade_type_info),
    path('get_trade_type_all_name/', views.get_trade_type_all_name),
    # 返回支付二维码
    path('get_order_status/', views.get_order_status),
    path('invoice/', views.invoice),
    path('add_card/', views.add_card),
    path('add_n_card/', views.add_n_card),
    path('get_card_info/', views.get_card_info),
    path('update_trade_type/', views.update_trade_type),
    path('query_trade_type/', views.query_trade_type),
    path('add_trade_type/', views.add_trade_type),
    path('pay_return/', views.pay_return),
    path('card_recharge/', views.card_recharge),
    path('get_pay_new_qr_code/', views.get_pay_new_qr_code),
    path('get_card/', views.get_card),
    path('update_card/', views.update_card),
    path('export_card/', views.export_card),
    path('export_financial_manager_excel/', views.export_financial_manager_excel),
    path('public_transfer/', views.public_transfer),
]
