list_rack = []
for i in range (36):
    print(i)
    i = i+1
    input_str = str(i)+'-1-U'
    list_rack.append(input_str)
    input_str = str(i)+'-1-D'
    list_rack.append(input_str)
    i = i+1

print(list_rack)
# for a in range(36):
#     a = a+1
#     str(a)+'-1-U'
#     a = a+1
# for a in range(36):
#     a = a+1
#     str(a)+'-1-D'
#     a = a+1
