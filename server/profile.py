
times = {
    'gathering' : 0.0,
    'analysis' : 0.0,
    'push' : 0.0,
    'save' : 0.0,
    'weather' : 0.0,
    'connection' : 0.0,
    'overall' : 0.0
    }

total = {
    'gathering' : 0.0,
    'analysis' : 0.0,
    'push' : 0.0,
    'save' : 0.0,
    'weather' : 0.0,
    'connection' : 0.0,
    'overall' : 0.0
    }


def do_stuff():
    for k,v in times.items():
        times[k] = times[k] / times['overall']
        total[k] = total[k] + times[k]

def init_times():
    times = {
        'gathering' : 0.0,
        'analysis' : 0.0,
        'push' : 0.0,
        'save' : 0.0,
        'weather' : 0.0,
        'connection' : 0.0,
        'overall' : 0.0
        }

def compute_overall():
    for k in total.keys():
        if k != 'overall':
            total[k] = total[k] / total['overall']

def main():
    init_times()
    with open('times.txt', 'r') as file:        
        for line in file:
            data = line.split(' : ')
            times[data[0]] = times.get(data[0],0.0) + float(data[1])
            if data[0] == 'overall':
                do_stuff()
                init_times()
    compute_overall()
    for k in total.keys():
         if k != 'overall':
             print( k+" : "+str(total[k]*100) )

if __name__ == '__main__':
    main()
