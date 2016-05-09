from multiprocessing import Process
import os
import sys


def get_category_dict(start, end):
    file = open('../conversion_codes.csv')
    json = {}
    rows = file.readlines()[start:end]
    for row in rows:
        code, cat, done = row.strip().split(',')
        code = code.strip()
        cat = cat.strip()
        done = done.strip()
        if cat == '':
            cat = code
        if done == '1':
            continue
        elif cat in json.keys():
            json[cat].append(code)
        else:
            json[cat] = [code]
    return json

def code(category, code):
    print("processing: " + category + ":" + code)
    command = 'python search.py ' + code + ' "' + category + '" ' + 'p'+code[0].lower()
    print(command)
    # os.system(command)
    print("finished process for " + code)

def codes(category, codes):
    for c in codes:
        p = Process(target=code, args=(category, c,))
        p.start()
        p.join()


if __name__ == '__main__':
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    categories = get_category_dict(start, end)
    # print(categories)
    pool = []
    for cat in categories:
        p = Process(target=codes, args=(cat, categories[cat],))
        p.start()
        pool.append(p)
    for p in pool:
        p.join()
