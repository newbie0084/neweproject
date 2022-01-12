import pickle
import datetime
import sys

# data = {인덱스(날짜):['입고일','위치','분류','세대','품명','규격','수량','현장명','비고','수정일']}
#data = {day_idx:[p_im_day,p_loc,p_type,p_gen,p_name,p_spec,p_qun,p_con_loc,p_memo,rev_date]}
now = datetime.datetime.now()
print(now)
now_time = str(now)[11:-7]
now_time = now_time.replace(':','-')
pico_sec = str(now)[-6:]
now_data = str(now)[:10]+'-'+now_time+pico_sec
now_data = now_data.replace('-','')
print(now_data)
data = {}
data['20220110094532599466'] = ['2020-02-10','1층_생산실','방열판','FL4','방열판1','회색','123','현장1','비고1','2022-01-10']
data['20220110094537838676'] = ['2020-03-10','2층_창고','모듈','FL2','모듈2','120W','123','현장2','비고2','2022-01-10']
data['20220110094625095137'] = ['2021-11-10','1층_생산창고','렌즈','FL3','렌즈3','회색','123','현장3','비고3','2022-01-10']
now_data = str(now)[:10]

print(now_data)
with open('../static/hs_data/hs_wh/hs_wh_'+now_data+'.pickle', 'wb') as f:
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


with open('../static/hs_data/hs_wh/hs_wh_'+now_data+'.pickle', 'rb') as f:
    load_data = pickle.load(f)

print(load_data)

if '20220110094625095131' in data.keys():
    print('ab')