from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "erptest"

urlpatterns = [
    # 메인
        path('',views.main,name='main'),

    # 재고 현황
        path('m_p_stock_location/',views.m_p_stock_location,name='m_p_stock_location'), #위치순

    #자재목록
        path('m_p_list/',views.m_p_list,name='m_p_list'),
        path('add_p_data/',views.add_p_data,name='add_p_data'),

    #입고/출고/반환
        path('m_import2/',views.m_import2,name='m_import2'),
        path('add_import/',views.add_import,name='add_import'),

        path('m_export2/',views.m_export2,name='m_export2'),
        path('add_export/',views.add_export,name='add_export'),

        path('m_return/',views.m_return,name='m_return'),



        
    # 로그인/아웃
        # path('',views.home,name='home'),
        path('register/', views.register),
        path('login/', views.login),
        path('logout/', views.logout),
        path('userpage/', views.userpage),
        path('managepage/', views.managepage),
        path('ch_p_page/', views.ch_p_page),
        path('ch_pass/', views.ch_pass,name='ch_pass'),

]

# if settings.DEBUG: 
#     urlpatterns += static(
#         settings.MEDIA_URL, 
#         document_root = settings.MEDIA_ROOT
#     )