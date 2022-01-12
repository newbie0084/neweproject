import pickle
import datetime
import sys
# {{자재명리스트.0~끝번호}}
# data = {'0-0': ['자재명', '현장명', '수량', '입고일', '비고']}
idx_no = "hs_0000_00_00_00"
data = {}
for a in range(36):
    a = a+1
    data[str(a)+'-1-U'] = ['자재명-'+str(a)+'-1-U', '현장명-'+str(a)+'-1-U', '수량-'+str(a)+'-1-U', '2021-11-23', '비고-'+str(a)+'-1-U']
    a = a+1
for a in range(36):
    a = a+1
    data[str(a)+'-1-D'] = ['자재명-'+str(a)+'-1-D', '현장명-'+str(a)+'-1-D', '수량-'+str(a)+'-1-D', '2021-11-23', '비고-'+str(a)+'-1-D']
    a = a+1
# print(data)
    
now = datetime.datetime.now()
print(now)
now_time = str(now)[11:-7]
now_time = now_time.replace(':','-')

now_data = str(now)[:10]+'-'+now_time
print(now_data)
now_data = now_data.replace('-','_')
print(now_data)
# # print(now_data)
# with open('../static/ware_state_st/w_st_'+now_data+'.pickle', 'wb') as f:
#     pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


# with open('../static/ware_state_st/w_st_'+now_data+'.pickle', 'rb') as f:
#     data = pickle.load(f)

# s_data = {}
# # print(data)
# if '1-1-D' in data:
#     s_data = data['1-1-D']
# else:
#     print('1234')

# print(s_data)
# print(data.keys())
