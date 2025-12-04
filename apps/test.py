batch_size = 32

arr = list(range(100))

for i in range(0, len(arr), batch_size):
    print(arr[i:i+batch_size])
