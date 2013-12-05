"""
profile.py performs the profiling of the different
sections of the application
"""

times = {
    'gathering': 0.0,
    'analysis': 0.0,
    'push': 0.0,
    'save': 0.0,
    'weather': 0.0,
    'connection': 0.0,
    'overall': 0.0
    }

total = {
    'gathering': 0.0,
    'analysis': 0.0,
    'push': 0.0,
    'save': 0.0,
    'weather': 0.0,
    'connection': 0.0,
    'overall': 0.0
    }


def run():
    for key, _ in times.items():
        times[key] = times[key] / times['overall']
        total[key] = total[key] + times[key]


def init_times():
    times = {
        'gathering': 0.0,
        'analysis': 0.0,
        'push': 0.0,
        'save': 0.0,
        'weather': 0.0,
        'connection': 0.0,
        'overall': 0.0
        }


def compute_overall():
    for k in total.keys():
        if k != 'overall':
            total[k] = total[k] / total['overall']


def main():
    with open('times.txt', 'r') as times_file:
        for line in times_file:
            data = line.split(' : ')
            times[data[0]] = times.get(data[0], 0.0) + float(data[1])
            if data[0] == 'overall':
                run()
                init_times()
    compute_overall()
    for k in total.keys():
        if k != 'overall':
            print(k+" : "+str(total[k]*100))


if __name__ == '__main__':
    main()
