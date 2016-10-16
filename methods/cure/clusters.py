from cure_new import *
import csv
from multiprocessing import Pool
import time

ended = 0

results = []
def processing(origin_data):
    cure_object = cure(origin_data, 5)
    cure_object.process()
    processing_results = cure_object.get_clusters()
    return processing_results


def resultCollector(result):
    global ended
    ended += 1
    results.append(result)


def main():
    data = []
    with open("Data10.csv", mode="r") as fh:

        readed_data = csv.reader(fh, delimiter=',')
        for row in readed_data:
            temp_data = []
            for j in range(len(row)):
                if j == 0:
                    continue
                cell = float(row[j])
                temp_data.append(cell)
                if j == 400:
                    break
            data.append(temp_data)
    start_time = time.time()
    cure_object = cure(data, 5)
    cure_object.process()
    print (cure_object.get_clusters())
    print "Execution time (sequential): ", time.time() - start_time

    start_time = time.time()
    ratio = int(len(data) / 5)

    chunks=[data[x:x+ratio] for x in xrange(0, len(data), ratio)]

    pool = Pool()
    for c_n in range(5):
        pool.apply_async(processing, args=(chunks[c_n],), callback=resultCollector)
    pool.close()
    pool.join()
    while ended != 5:
        pass
    common_list = []
    for result in results:
        common_list += result
    final_cure_object = cure(common_list, 5, pre_processed=True)
    final_cure_object.process()
    result = final_cure_object.get_clusters() + '\n'
    result += "Execution time (parallel): ", time.time() - start_time
    return result
