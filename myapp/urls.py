from django.urls import path
from .views import *
urlpatterns = [
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('register/', RegisterView.as_view(), name='register'),
    path('rolemaster/', MasterRoleView.as_view(), name='role_masters'),
    path('login/', LoginView.as_view(), name='login'),
    path('change_password/', OTPChangePassword.as_view(), name='change_password'),
    path('sendOTP/', SendOTP.as_view(), name='SendOTP'),
    path('selling/', SellerProcess.as_view(), name='SellerProcess'),
    path('buying/', BuyerProcess.as_view(), name='BuyerProcess'),
    path('admin/product_view/', CateoriesProducts.as_view(), name='CateoriesProducts'),
    path('ExcelDatas/', ExcelDatas.as_view(), name='ExcelDatas'),    
    # path('view_products/', SellerProcess.as_view(), name='view_products'), 
    # path('selling/', SellerProcess.as_view(), {'download_pdf': True}, name='download_pdf'),
]
