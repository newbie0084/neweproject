from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
import pickle
# import sys
import datetime
import copy
from matplotlib import font_manager, rc
from matplotlib import style
from operator import itemgetter
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# 로그인
from django.contrib.auth.hashers import make_password,check_password #패스워드 비교를 위한 참조 
from .forms import LoginForm
from django import forms
from .models import Document, Fuser #DB의 Fuser와 데이터 비교를 위한 참조
from django.contrib import messages
import openpyxl
from . import models

from django.conf import settings
from django.core.files.storage import FileSystemStorage

import shutil #파일복사
import json

    
# ==============================================================
#                          메인
# ==============================================================

def main(request):

    return render(request,'login/home.html')

# ==============================================================
#                         로그인
# ==============================================================

# 회원가입
def register(request):
    
    puser = Fuser.objects.all()
    userlist = []
    for i in range(len(puser)):
        userlist.append(puser[i].username)

    chk_user = 0

    if request.method == "POST":
        #여기에 회원가입 처리 코드
        # username = request.POST['username']
        # password = request.POST['password']
        # re_password = request.POST['re-password']
      
        username = request.POST.get('username',None)
        name_hs = request.POST.get('name_hs',None)
        password = request.POST.get('password',None)
        re_password = request.POST.get('re-password',None)


        res_data ={} #프론트에 던져줄 응답 데이터

        for i in userlist:
            if username == i:
                chk_user=1


        #모든 값을 입력해야됨
        if not( username and name_hs and password and re_password): #None은 False로 인식
            res_data['error']="모든 값을 입력해야합니다."
        #비밀번호가 다르면 리턴
        elif password != re_password:
            # return HttpResponse("비밀번호가 다름")
            res_data['error']="비밀번호가 다름"
        #같으면 저장

        elif chk_user == 1:
            res_data['error']="중복아이디"
        else : 
            #위 정보들로 인스턴스 생성
            fuser = Fuser(
                username= username,
                name_hs= name_hs,
                password= make_password(password),
                permission_u = '1',
            )
            
            #저장
            fuser.save()
            form = LoginForm()
            messages.info(request, '회원가입완료!!')
            return redirect('/login/',{'form':form})

        return render(request, 'login/register.html',res_data)
        
    else:
        return render(request, 'login/register.html')

# 로그인
def login(request):


    if request.method =="POST":
        form = LoginForm(request.POST)
        #정상적인 데이터인지 확인
        if form.is_valid(): #forms.py에 정의한 clean 메소드대로 검증한다.
            #로그인 session 추가
            request.session['user'] = form.user_id #매칭된 fuser모델의 pk를 세션.user로 추가

            return redirect('/userpage/') #루트 페이지로 리다이렉트
    else:
        form = LoginForm()

    return render(request,'login/login.html',{'form':form}) #응답 데이터 res_data 전달

# 로그아웃
def logout(request):
    user_pk = request.session.get('user')
    
    if user_pk: #세션에 user_pk 정보가 존재하면
        if request.session['user'] : #로그인 중이라면
            del(request.session['user'])

    return redirect('/') #홈으로

# 유저페이지
def userpage(request):
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # print(ip)

    

    now = datetime.datetime.now()           # 오늘 날짜



    now_time = str(now)[:22]
    print(now)
    print(ip)

    file = open('static/logs/ip_logs.txt','a',encoding='UTF-8')


    user_pk = request.session.get('user')
    error = ''
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        if fuser.permission_u == '1':
            w_message = '등급 1 / '+fuser.username +' / 환영합니다.'
            url = 'login/newbie_u_page.html'

            file.write("\\" +now_time + " :>> "+fuser.username+" || "+ip+"\n")
            file.close()
        elif fuser.permission_u == '2':
            w_message = '등급 2 / '+fuser.username +' / 환영합니다.'
            url = 'login/manager_u_page.html'

            file.write("\\ " +now_time + " :>> "+fuser.username+" || "+ip+"\n")
            file.close()
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            file.write("\\ " +now_time + " :>> wrong contect || "+ip+"\n")
            file.close()
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
        return render(request,url,{'w_message':w_message})
    error = '로그인 하십시오.'
    file.write("\\ " +now_time + " :>> wrong contect || "+ip+"\n")
    file.close()
    return render(request,'login/userpage.html',{'error':error})

# 관리페이지 이동
def managepage(request):
    
    user_pk = request.session.get('user')
    error = ''
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
            redirect('/itemmain/')
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
        return render(request,url,{'w_message':w_message})
    error = '로그인 하십시오.'
    return render(request,'login/userpage.html',{'error':error})

# 비번변경페이지
@csrf_exempt
def ch_p_page(request):
    user_pk = request.session.get('user')
    error = ''
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        if fuser.permission_u == '1':
            w_message = '등급 1 / '+fuser.username +' / 비밀번호변경'
            url = 'login/ch_pass.html'
        elif fuser.permission_u == '2':
            w_message = '등급 2 / '+fuser.username +' / 비밀번호변경'
            url = 'login/ch_pass.html'
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
        return render(request,url,{'w_message':w_message})
    error = '로그인 하십시오.'
    return render(request,'login/userpage.html',{'error':error})

# 비번변경
@csrf_exempt
def ch_pass(request):
    user_pk = request.session.get('user')
    error = ''
    print('asdf')
    n_pass = request.POST['n_pass']
    
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        if fuser.permission_u == '1':
            fuser = Fuser.objects.get(pk=user_pk)
            fuser.password = make_password(n_pass)
            fuser.save()
            w_message = '등급 1 / '+fuser.username +' / 환영합니다.'
            url = 'login/newbie_u_page.html'
            error = '비밀번호 변경 완료'
        elif fuser.permission_u == '2':
            fuser = Fuser.objects.get(pk=user_pk)
            fuser.password = make_password(n_pass)
            fuser.save()
            w_message = '등급 2 / '+fuser.username +' / 환영합니다.'
            url = 'login/manager_u_page.html'
            error = '비밀번호 변경 완료'
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
        return render(request,url,{'w_message':w_message,'error':error})
    error = '로그인 하십시오.'

    return render(request,'login/userpage.html',{'error':error})

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#재고현황 위치별 분류 필요
@csrf_exempt
def m_p_stock_location(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})

    
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    now = datetime.datetime.now()           # 오늘 날짜

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # print('현재 데이터')
    # print(ori_data)

    ori_data_keys = list(ori_data.keys())
    data_ori_list = []
    
    for i in ori_data_keys:
        dic_lsit = []
        dic_lsit.append(i)
        for j in ori_data[i]:
            dic_lsit.append(j)
        data_ori_list.append(dic_lsit)
    
    # print('+++++++++++++++++++++++++++')
    # print('현재 데이터 리스트화')
    # print(data_ori_list)
    # print('+++++++++++++++++++++++++++')

    # sorted_data = sorted(ori_data.items(), key=lambda x: x[1][9])
    # print('데이터 정렬')
    # print(sorted_data)

    
    
    index = 0
    index_list = []

    day_idx_list = []
    p_im_day_list = []
    p_loc_list = []
    p_type_list = []
    p_gen_list = []
    p_name_list = []
    p_spec_list = []
    p_qun_list = []
    p_con_loc_list = []
    p_memo_list = []
    rev_date_list = []
    

    # [day_idx] = [p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo]
    for onelist in data_ori_list:
        index_list.append(index)
        day_idx_list.append(onelist[0])
        p_im_day_list.append(onelist[1])
        p_loc_list.append(onelist[2])
        p_type_list.append(onelist[3])
        p_gen_list.append(onelist[4])
        p_name_list.append(onelist[5])
        p_spec_list.append(onelist[6])
        p_qun_list.append(onelist[7])
        p_con_loc_list.append(onelist[8])
        p_memo_list.append(onelist[9])
        rev_date_list.append(onelist[10])
        index+=1
    len_idx = len(index_list)
    # print(index)

    jlist = []
    jlist = p_loc_list
    dump_list = json.dumps(jlist)

    my_set = set(p_loc_list)
    place_list = list(my_set)
    place_list.sort()


            
    return render(request,'material/m_p_stock_location.html',{'l_id':l_id,
                                                    'l_name':l_name,
                                                    'index_list':index_list,
                                                    'day_idx_list':day_idx_list,
                                                    'p_im_day_list':p_im_day_list,
                                                    'p_loc_list':p_loc_list,
                                                    'p_type_list':p_type_list,
                                                    'p_gen_list':p_gen_list,
                                                    'p_name_list':p_name_list,
                                                    'p_spec_list':p_spec_list,
                                                    'p_qun_list':p_qun_list,
                                                    'p_con_loc_list':p_con_loc_list,
                                                    'p_memo_list':p_memo_list,
                                                    'rev_date_list':rev_date_list,
                                                    'len_idx':len_idx,
                                                    'jlist_test':dump_list})

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#자재목록
def m_p_list(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})


    
    path_dir = 'static/hs_data/hs_p_data/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_p_data' in f_o:
            file_list.append(f_o)

    file_list.sort()

    now = datetime.datetime.now()           # 오늘 날짜

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # print('현재 데이터')
    # print(ori_data)

    ori_data_keys = list(ori_data.keys())
    data_ori_list = []
    
    for i in ori_data_keys:
        dic_lsit = []
        dic_lsit.append(i)
        for j in ori_data[i]:
            dic_lsit.append(j)
        data_ori_list.append(dic_lsit)
    
    # print('+++++++++++++++++++++++++++')
    # print('현재 데이터 리스트화')
    # print(data_ori_list)
    # print('+++++++++++++++++++++++++++')

    sorted_data = sorted(ori_data.items(), key=lambda x: x[1][9])
    # print('데이터 정렬')
    # print(sorted_data)

    
    
    index = 0
    index_list = []

    pn_list = []

    p_name_list = []
    p_gen_list = []
    p_usage_list = []
    p_type_list = []
    p_angle_list = []
    p_watt_list = []
    p_l_type_list = []
    p_c_t_list = []
    p_com_list = []
    p_spec_list = []
    p_memo_list = []
    

    # [day_idx] = [p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo]
    for onelist in data_ori_list:
        index_list.append(index)
        pn_list.append(onelist[0])
        p_name_list.append(onelist[1])
        p_gen_list.append(onelist[2])
        p_usage_list.append(onelist[3])
        p_type_list.append(onelist[4])
        p_angle_list.append(onelist[5])
        p_watt_list.append(onelist[6])
        p_l_type_list.append(onelist[7])
        p_c_t_list.append(onelist[8])
        p_com_list.append(onelist[9])
        p_spec_list.append(onelist[10])
        p_memo_list.append(onelist[11])
        index+=1
    len_idx = len(index_list)
    # print(index)

            
    return render(request,'material/m_p_list.html',{'l_id':l_id,
                                                    'l_name':l_name,
                                                    'index_list':index_list,
                                                    'pn_list':pn_list,
                                                    'p_name_list':p_name_list,
                                                    'p_gen_list':p_gen_list,
                                                    'p_usage_list':p_usage_list,
                                                    'p_type_list':p_type_list,
                                                    'p_angle_list':p_angle_list,
                                                    'p_watt_list':p_watt_list,
                                                    'p_l_type_list':p_l_type_list,
                                                    'p_c_t_list':p_c_t_list,
                                                    'p_com_list':p_com_list,
                                                    'p_spec_list':p_spec_list,
                                                    'p_memo_list':p_memo_list,
                                                    'len_idx':len_idx})


#자재 등록v
@csrf_exempt
def add_p_data(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})
            
            
                        # p_ind:p_ind,
                        # p_type:p_type,
                        # ps_position:ps_position,
                        # p_name:p_name,
                        # import_num:import_num,
                        # construction_site:construction_site,
                        # p_memo:p_memo
    # 데이터불러오기
    p_name = request.POST['p_name']
    p_gen = request.POST['p_gen']
    p_usage = request.POST['p_usage']
    p_type = request.POST['p_type']
    p_angle = request.POST['p_angle']
    p_watt = request.POST['p_watt']
    p_l_type = request.POST['p_l_type']
    p_c_t = request.POST['p_c_t']
    p_com = request.POST['p_com']
    p_spec = request.POST['p_spec']
    p_memo = request.POST['p_memo']

    now = datetime.datetime.now()           # 오늘 날짜
    print(now)
    now_time = str(now)[11:-7]
    now_time = now_time.replace(':','-')
    pico_sec = str(now)[-6:]
    now_data = str(now)[:10]+'-'+now_time+pico_sec
    now_data = now_data.replace('-','')
    now_data = 'HS-'+now_data

    pnamespec = p_name.split('||')
    
    in_data = {}
    in_data[now_data] = []
    print(in_data)

    path_dir = 'static/hs_data/hs_p_data/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_p_data' in f_o:
            file_list.append(f_o)

    file_list.sort()

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    
    ori_data[now_data] = [p_name,p_gen,p_usage,p_type,p_angle,p_watt,p_l_type,p_c_t,p_com,p_spec,p_memo]

    now_data = str(now)[:10]
    
    print(now_data)
    with open('static/hs_data/hs_p_data/hs_p_data_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(ori_data, f, pickle.HIGHEST_PROTOCOL)

    # print('saved!')
    return redirect('/m_p_list/')
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
#입고 페이지v
def m_import2(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})

    
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    now = datetime.datetime.now()           # 오늘 날짜

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # print('현재 데이터')
    # print(ori_data)

    ori_data_keys = list(ori_data.keys())
    data_ori_list = []
    
    for i in ori_data_keys:
        dic_lsit = []
        dic_lsit.append(i)
        for j in ori_data[i]:
            dic_lsit.append(j)
        data_ori_list.append(dic_lsit)
    
    # print('+++++++++++++++++++++++++++')
    # print('현재 데이터 리스트화')
    # print(data_ori_list)
    # print('+++++++++++++++++++++++++++')

    sorted_data = sorted(ori_data.items(), key=lambda x: x[1][9])
    # print('데이터 정렬')
    # print(sorted_data)

    
    
    index = 0
    index_list = []

    day_idx_list = []
    p_im_day_list = []
    p_loc_list = []
    p_type_list = []
    p_gen_list = []
    p_name_list = []
    p_spec_list = []
    p_qun_list = []
    p_con_loc_list = []
    p_memo_list = []
    rev_date_list = []
    

    # [day_idx] = [p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo]
    for onelist in data_ori_list:
        index_list.append(index)
        day_idx_list.append(onelist[0])
        p_im_day_list.append(onelist[1])
        p_loc_list.append(onelist[2])
        p_type_list.append(onelist[3])
        p_gen_list.append(onelist[4])
        p_name_list.append(onelist[5])
        p_spec_list.append(onelist[6])
        p_qun_list.append(onelist[7])
        p_con_loc_list.append(onelist[8])
        p_memo_list.append(onelist[9])
        rev_date_list.append(onelist[10])
        index+=1
    len_idx = len(index_list)
    # print(index)

    jlist = []
    jlist = p_loc_list
    dump_list = json.dumps(jlist)
            
    return render(request,'material/m_import2.html',{'l_id':l_id,
                                                    'l_name':l_name,
                                                    'index_list':index_list,
                                                    'day_idx_list':day_idx_list,
                                                    'p_im_day_list':p_im_day_list,
                                                    'p_loc_list':p_loc_list,
                                                    'p_type_list':p_type_list,
                                                    'p_gen_list':p_gen_list,
                                                    'p_name_list':p_name_list,
                                                    'p_spec_list':p_spec_list,
                                                    'p_qun_list':p_qun_list,
                                                    'p_con_loc_list':p_con_loc_list,
                                                    'p_memo_list':p_memo_list,
                                                    'rev_date_list':rev_date_list,
                                                    'len_idx':len_idx,
                                                    'jlist_test':dump_list})
    

#입고 등록v
@csrf_exempt
def add_import(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})
            
            
                        # p_ind:p_ind,
                        # p_type:p_type,
                        # ps_position:ps_position,
                        # p_name:p_name,
                        # import_num:import_num,
                        # construction_site:construction_site,
                        # p_memo:p_memo
    # 데이터불러오기
    p_ind = request.POST['p_ind']
    p_type = request.POST['p_type']
    ps_position = request.POST['ps_position']
    p_name = request.POST['p_name']
    import_num  = request.POST['import_num']
    construction_site = request.POST['construction_site']
    p_memo = request.POST['p_memo']
    rev_date_input = request.POST['rev_date_input']
    day_idx_ex = request.POST['day_idx_ex']
    
    now = datetime.datetime.now()           # 오늘 날짜
    now_time = str(now)[11:-7]
    now_time = now_time.replace(':','-')
    pico_sec = str(now)[-6:]
    now_data = str(now)[:10]+'-'+now_time+pico_sec
    now_data = now_data.replace('-','')

    pnamespec = p_name.split('||')
    
    in_data = {}
    in_data[now_data] = [p_ind,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],import_num,construction_site,p_memo,rev_date_input]
    # print(in_data)
    # ++++++++++++++++++++++재고 저장 데이터불러오기
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    data = {}
    ori_data = {}#원데이터

    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # ++++++++++++++++++++++입고 저장 데이터불러오기
    path_dir_2 = 'static/hs_data/hs_import/'
    file_lists_2 = os.listdir(path_dir_2)
    file_lists_2.sort()

    file_list_2=[]
    for f_o in file_lists_2:
        if 'import_data' in f_o:
            file_list_2.append(f_o)

    file_list_2.sort()

    add_ori_data = {}
    add_data = {}#원데이터

    with open(path_dir_2+file_list_2[-1], 'rb') as f:
        add_ori_data = copy.deepcopy(pickle.load(f))

    add_data = copy.deepcopy(add_ori_data)
    tri_str = ''
    if day_idx_ex in ori_data.keys():
        change_num = int(ori_data[day_idx_ex][6])+int(import_num)
        ori_data[day_idx_ex] = [p_ind,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],change_num,construction_site,p_memo,rev_date_input]
        tri_str = '기존입고'
    else:
        ori_data[now_data] = [p_ind,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],import_num,construction_site,p_memo,rev_date_input]
        tri_str = '신규입고'
    # ori_data_keys = list(ori_data.keys())
    # print(ori_data.keys())
    # data_ori_list = []
    # print(ori_data)
    add_data_add = str(now)[:19]
    add_data[add_data_add] = [now_data,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],import_num,construction_site,p_memo,rev_date_input,tri_str]

    now_data = str(now)[:10]
    print(add_data)
    print(now_data)
    with open('static/hs_data/hs_wh/hs_wh_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(ori_data, f, pickle.HIGHEST_PROTOCOL)

    with open(path_dir_2+'import_data_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(add_data, f, pickle.HIGHEST_PROTOCOL)

    # print('saved!')
    return redirect('/m_import2/')


#입고 삭제v
@csrf_exempt
def add_import(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})
            
            
    day_idx_ex = request.POST['day_idx_ex']
    
    now = datetime.datetime.now()           # 오늘 날짜
    now_time = str(now)[11:-7]
    now_time = now_time.replace(':','-')
    pico_sec = str(now)[-6:]
    now_data = str(now)[:10]+'-'+now_time+pico_sec
    now_data = now_data.replace('-','')

    # ++++++++++++++++++++++재고 저장 데이터불러오기
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    data = {}
    ori_data = {}#원데이터

    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # ++++++++++++++++++++++입고 저장 데이터불러오기

    del ori_data[day_idx_ex]

    with open('static/hs_data/hs_wh/hs_wh_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(ori_data, f, pickle.HIGHEST_PROTOCOL)

    # print('saved!')
    return redirect('/m_import2/')
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#출고v
def m_export2(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})

    
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    now = datetime.datetime.now()           # 오늘 날짜

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # print('현재 데이터')
    # print(ori_data)

    ori_data_keys = list(ori_data.keys())
    data_ori_list = []
    
    for i in ori_data_keys:
        dic_lsit = []
        dic_lsit.append(i)
        for j in ori_data[i]:
            dic_lsit.append(j)
        data_ori_list.append(dic_lsit)
    
    # print('+++++++++++++++++++++++++++')
    # print('현재 데이터 리스트화')
    # print(data_ori_list)
    # print('+++++++++++++++++++++++++++')

    sorted_data = sorted(ori_data.items(), key=lambda x: x[1][9])
    # print('데이터 정렬')
    # print(sorted_data)

    
    
    index = 0
    index_list = []

    day_idx_list = []
    p_im_day_list = []
    p_loc_list = []
    p_type_list = []
    p_gen_list = []
    p_name_list = []
    p_spec_list = []
    p_qun_list = []
    p_con_loc_list = []
    p_memo_list = []
    rev_date_list = []
    

    # [day_idx] = [p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo]
    for onelist in data_ori_list:
        index_list.append(index)
        day_idx_list.append(onelist[0])
        p_im_day_list.append(onelist[1])
        p_loc_list.append(onelist[2])
        p_type_list.append(onelist[3])
        p_gen_list.append(onelist[4])
        p_name_list.append(onelist[5])
        p_spec_list.append(onelist[6])
        p_qun_list.append(onelist[7])
        p_con_loc_list.append(onelist[8])
        p_memo_list.append(onelist[9])
        rev_date_list.append(onelist[10])
        index+=1
    len_idx = len(index_list)
    # print(index)
            
    return render(request,'material/m_export2.html',{'l_id':l_id,
                                                    'l_name':l_name,
                                                    'index_list':index_list,
                                                    'day_idx_list':day_idx_list,
                                                    'p_im_day_list':p_im_day_list,
                                                    'p_loc_list':p_loc_list,
                                                    'p_type_list':p_type_list,
                                                    'p_gen_list':p_gen_list,
                                                    'p_name_list':p_name_list,
                                                    'p_spec_list':p_spec_list,
                                                    'p_qun_list':p_qun_list,
                                                    'p_con_loc_list':p_con_loc_list,
                                                    'p_memo_list':p_memo_list,
                                                    'rev_date_list':rev_date_list,
                                                    'len_idx':len_idx})
    

#출고 등록 #변경필요
@csrf_exempt
def add_export(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})
            
            
                        # p_ind:p_ind,
                        # p_type:p_type,
                        # ps_position:ps_position,
                        # p_name:p_name,
                        # import_num:import_num,
                        # construction_site:construction_site,
                        # p_memo:p_memo
    # 데이터불러오기
    p_ind = request.POST['p_ind']
    p_type = request.POST['p_type']
    ps_position = request.POST['ps_position']
    p_name = request.POST['p_name']
    import_num  = request.POST['import_num']
    construction_site = request.POST['construction_site']
    p_memo = request.POST['p_memo']
    rev_date_input = request.POST['rev_date_input']
    day_idx_ex = request.POST['day_idx_ex']
    
    now = datetime.datetime.now()           # 오늘 날짜
    now_time = str(now)[11:-7]
    now_time = now_time.replace(':','-')
    pico_sec = str(now)[-6:]
    now_data = str(now)[:10]+'-'+now_time+pico_sec
    now_data = now_data.replace('-','')

    pnamespec = p_name.split('||')
    
    in_data = {}
    in_data[now_data] = [p_ind,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],import_num,construction_site,p_memo,rev_date_input]
    # print(in_data)
    # ++++++++++++++++++++++재고 저장 데이터불러오기
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    data = {}
    ori_data = {}#원데이터

    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # ++++++++++++++++++++++입고 저장 데이터불러오기
    path_dir_2 = 'static/hs_data/hs_export/'
    file_lists_2 = os.listdir(path_dir_2)
    file_lists_2.sort()

    file_list_2=[]
    for f_o in file_lists_2:
        if 'export_data' in f_o:
            file_list_2.append(f_o)

    file_list_2.sort()

    add_ori_data = {}
    add_data = {}#원데이터

    with open(path_dir_2+file_list_2[-1], 'rb') as f:
        add_ori_data = copy.deepcopy(pickle.load(f))

    add_data = copy.deepcopy(add_ori_data)
    tri_str = ''
    # print('aa')
    # print(ori_data)
    # print('bb')
    # print(day_idx_ex)

    change_num = int(ori_data[day_idx_ex][6])-int(import_num)
    ori_data[day_idx_ex] = [p_ind,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],change_num,construction_site,p_memo,rev_date_input]
    tri_str = '기존출고'
    # ori_data_keys = list(ori_data.keys())
    # print(ori_data.keys())
    # data_ori_list = []
    # print(ori_data)
    add_data_add = str(now)[:19]
    add_data[add_data_add] = [now_data,ps_position,pnamespec[0],'',pnamespec[1],pnamespec[2],import_num,construction_site,p_memo,rev_date_input,tri_str]

    now_data = str(now)[:10]
    # print(add_data)
    # print(now_data)
    with open('static/hs_data/hs_wh/hs_wh_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(ori_data, f, pickle.HIGHEST_PROTOCOL)

    with open(path_dir_2+'export_data_'+now_data+'.pickle', 'wb') as f:
        pickle.dump(add_data, f, pickle.HIGHEST_PROTOCOL)

    # print('saved!')
    return redirect('/m_export2/')
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#반환
def m_return(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})

    
    path_dir = 'static/hs_data/hs_wh/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'hs_wh' in f_o:
            file_list.append(f_o)

    file_list.sort()

    now = datetime.datetime.now()           # 오늘 날짜

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    # print('현재 데이터')
    # print(ori_data)

    ori_data_keys = list(ori_data.keys())
    data_ori_list = []
    
    for i in ori_data_keys:
        dic_lsit = []
        dic_lsit.append(i)
        for j in ori_data[i]:
            dic_lsit.append(j)
        data_ori_list.append(dic_lsit)
    
    # print('+++++++++++++++++++++++++++')
    # print('현재 데이터 리스트화')
    # print(data_ori_list)
    # print('+++++++++++++++++++++++++++')

    sorted_data = sorted(ori_data.items(), key=lambda x: x[1][9])
    # print('데이터 정렬')
    # print(sorted_data)

    
    
    index = 0
    index_list = []

    day_idx_list = []
    p_im_day_list = []
    p_loc_list = []
    p_type_list = []
    p_gen_list = []
    p_name_list = []
    p_spec_list = []
    p_qun_list = []
    p_con_loc_list = []
    p_memo_list = []
    rev_date_list = []
    

    # [day_idx] = [p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo]
    for onelist in data_ori_list:
        index_list.append(index)
        day_idx_list.append(onelist[0])
        p_im_day_list.append(onelist[1])
        p_loc_list.append(onelist[2])
        p_type_list.append(onelist[3])
        p_gen_list.append(onelist[4])
        p_name_list.append(onelist[5])
        p_spec_list.append(onelist[6])
        p_qun_list.append(onelist[7])
        p_con_loc_list.append(onelist[8])
        p_memo_list.append(onelist[9])
        rev_date_list.append(onelist[10])
        index+=1
    len_idx = len(index_list)
    # print(index)
            
    return render(request,'material/m_return.html',{'l_id':l_id,
                                                    'l_name':l_name,
                                                    'index_list':index_list,
                                                    'day_idx_list':day_idx_list,
                                                    'p_im_day_list':p_im_day_list,
                                                    'p_loc_list':p_loc_list,
                                                    'p_type_list':p_type_list,
                                                    'p_gen_list':p_gen_list,
                                                    'p_name_list':p_name_list,
                                                    'p_spec_list':p_spec_list,
                                                    'p_qun_list':p_qun_list,
                                                    'p_con_loc_list':p_con_loc_list,
                                                    'p_memo_list':p_memo_list,
                                                    'rev_date_list':rev_date_list,
                                                    'len_idx':len_idx})

#반환 등록
def m_return_add(request):

    # 로그인정보
    l_id = ''
    l_name = ''
    user_pk = request.session.get('user')
    if user_pk: #세션에 user_pk 정보가 존재하면
        fuser = Fuser.objects.get(pk=user_pk)
        l_id = fuser.username
        l_name = fuser.name_hs
        if fuser.permission_u == '1':
            error = '권한없음'
            url = 'login/newbie_u_page.html'
            return render(request,url,{'error':error})
        elif fuser.permission_u == '2':
            w_message = '등급 2 '+fuser.username
        else:
            w_message = 'who are you?'
            error = '???????????????????????????????'
            return render(request,'login/error_user_page.html',{'w_message':w_message,'error':error})
    else:
            return render(request,'login/error_user_page.html',{'w_message':'error','error':'error'})


    position_p = request.POST['position_p']  #키
    in_num  = request.POST['in_num']         #[4]
    p_memo = request.POST['p_memo']          #[8]


    now = datetime.datetime.now()           # 오늘 날짜

    # in_data[position_p] = [p_n,p_name,p_sp,c_name,in_num,c_place,lot_no,p_in_date,p_memo,str(now)[:10],p_type,img_add]


    path_dir = 'static/hs_data/hs_import/'
    file_lists = os.listdir(path_dir)
    file_lists.sort()

    file_list=[]
    for f_o in file_lists:
        if 'import_data' in f_o:
            file_list.append(f_o)

    file_list.sort()

    data = {}
    ori_data = {}#원데이터


    with open(path_dir+file_list[-1], 'rb') as f:
        data = copy.deepcopy(pickle.load(f))

    ori_data = copy.deepcopy(data)
    
    ori_data[position_p][4] = in_num
    ori_data[position_p][8] = p_memo
    print(ori_data)

    
    # with open(path_dir+'import_data'+str(now)[:9]+'.pickle', 'wb') as f:
    #     pickle.dump(ori_data, f, pickle.HIGHEST_PROTOCOL)

    # print('saved!')


            
    return render(request,'material/m_return.html',{'l_id':l_id,'l_name':l_name})

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    #이력조회
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


    
def sorted_ls(path):

    mtime=lambda f: os.stat(os.path.join(path, f)).st_mtime

    return list(sorted(os.listdir(path), key=mtime))