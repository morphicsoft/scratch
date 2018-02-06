

def batches(min_id, max_id, n):
    table_size = max_id - min_id
    size, rem = divmod(table_size, n)
    batches = ((min_id + (size * i), min_id + (size * i) + size + rem)
               if i == n-1 else
               (min_id + (size * i), min_id + (size * i) + size - 1)
               for i in range(n))
    return batches


for interval, id in zip(batches(100, 2100, 5), 'ABCDEF'):
    print("interval = {}, id = {}, size = {}".format(interval, id, interval[1]-interval[0]+1))

