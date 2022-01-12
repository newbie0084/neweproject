import pickle
import datetime
import sys

# data = {인덱스(날짜):['입고일','위치','분류','세대','품명','규격','변동수량','현장명','비고','수정한사람']}

now = datetime.datetime.now()
# print(str(now)[:19])
now_time = str(now)[11:-7]
now_time = now_time.replace(':','-')
pico_sec = str(now)[-6:]
now_data = str(now)[:10]+'-'+now_time+pico_sec
now_data = now_data.replace('-','')
# print(now_data)
data = {}
data['2020-02-10 15:13:46'] = ['20220110094532599466','1층_생산실','방열판','FL4','방열판1','회색','+123','현장1','비고1','2022-01-10','테스트입고']
data['2020-03-10 15:13:46'] = ['20220110094537838676','2층_창고','모듈','FL2','모듈2','120W','+123','현장2','비고2','2022-01-10','테스트입고']
data['2021-11-10 15:13:46'] = ['20220110094625095137','1층_생산창고','렌즈4','FL3','렌즈3','회색','+123','현장7','비고8','2022-01-12','테스트입고']
data['2021-02-10 15:13:46'] = ['20220110094625095122','1층_생산창고','렌즈2','FL3','렌즈2','회색','+123','현장3','비고2','2022-01-14','테스트입고']
data['2021-06-10 15:13:46'] = ['20220110094625094214','1층_생산창고','렌즈1','FL3','렌즈1','회색','+123','현장1','비고3','2022-01-21','테스트입고']
data['2021-09-10 15:13:46'] = ['20220110094625033321','1층_생산창고','렌즈3','FL3','렌즈5','회색','+123','현장9','비고1','2022-01-13','테스트입고']


# print(data)


data_1 = {}
data_2 = {}
data_3 = {}
data_4 = {}
data_5 = {}
data_6 = {}
data_7 = {}
data_8 = {}

for i in data:
    if data[i][1] == '1층_생산실':
        data_1[i] = data[i]
    elif data[i][1] == '1층_생산창고':
        data_2[i] = data[i]
    elif data[i][1] == '1층_AS창고':
        data_3[i] = data[i]
    elif data[i][1] == '1층_완제품창고':
        data_4[i] = data[i]
    elif data[i][1] == '2층_창고':
        data_5[i] = data[i]
    elif data[i][1] == '2층_자재창고':
        data_6[i] = data[i]
    elif data[i][1] == '3층_품질팀':
        data_7[i] = data[i]
    else:
        data_8[i] = data[i]

print(data_1)
print(data_2)
print(data_3)
print(data_4)
print(data_5)
print(data_6)
print(data_7)
print(data_8)

now_data = str(now)[:10]

# print(now_data)
# with open('../static/hs_data/hs_import/import_data_'+now_data+'.pickle', 'wb') as f:
#     pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


with open('../static/hs_data/hs_import/import_data_'+now_data+'.pickle', 'rb') as f:
    load_data = pickle.load(f)


for i in load_data:
    print(i)