import numpy as np
from functools import reduce
import math

class DetailItem:
    def __init__(self, machines_count, machines_processing, name=None):
        self.name = name
        self.machines_count = machines_count
        if not type(machines_processing) is list or len(machines_processing) != machines_count:
            raise Exception('Wrong machine processing time data')
        self.machines_processing = machines_processing

    @staticmethod
    def create_from_multiple_list(data_list):
        if len(data_list) == 0:
            raise Exception('Data list is empty')
        details_count = len(data_list[0, :])
        data = [DetailItem(len(data_list), data_list[:, i].tolist(), i+1) for i in range(details_count)]
        return data


class Johnson:
    def __init__(self, data):
        if not type(data) is list:
            raise Exception('Invalid data list')
        self.data = data

    def optimize(self):
        if all([i.machines_count == 2 for i in self.data]):
            return self.__johnson_method_2_machines()
        elif all([i.machines_count == 3 for i in self.data]):
            return self.__johnson_method_3_machines()

    @staticmethod
    def __sort(arr, cmp):
        while True:
            swapped = False
            for i in range(0, len(arr) - 1):
                if cmp(arr[i], arr[i+1]):
                    arr[i], arr[i+1] = arr[i+1], arr[i]
                    swapped = True
            if not swapped:
                break
        return arr

    def __johnson_method_2_machines(self):
        opt = Johnson.__sort(self.data, lambda a, b: min(a.machines_processing[0], b.machines_processing[1]) >
                            min(a.machines_processing[1], b.machines_processing[0]))
        return {
            'path': opt,
            'delay': Johnson.__find_sum_delay(opt),
            'duration': Johnson.__find_sum_duration(opt)
        }

    def __custom_johnson_method(self, comparator):
        return Johnson.__sort(self.data, comparator)

    def __johnson_method_3_machines(self):
        min_1st_machine = min([i.machines_processing[0] for i in self.data])
        min_3rd_machine = min([i.machines_processing[2] for i in self.data])
        max_2nd_machine = max([i.machines_processing[1] for i in self.data])

        if min_1st_machine >= max_2nd_machine:
            opt = self.__custom_johnson_method(lambda a, b: min(a.machines_processing[0] + a.machines_processing[1],
                                                                b.machines_processing[2]) >
                                                            min(a.machines_processing[2], b.machines_processing[0] +
                                                                b.machines_processing[1]))
        elif min_3rd_machine >= max_2nd_machine:
            opt = self.__custom_johnson_method(lambda a, b: min(a.machines_processing[0], b.machines_processing[1]
                                                                + b.machines_processing[2]) >
                                                            min(a.machines_processing[1] + a.machines_processing[2],
                                                                b.machines_processing[0]))
        else:
            opt = Johnson.__opt_cmb(self.data)['path']
        opt_params = Johnson.__calc_up_downtime(opt, 3)
        pass
        return {
            'path': opt,

        }

    @staticmethod
    def __calc_up_downtime(data, machine_count, prev_machine=0, tracing=None):
        if prev_machine + 1 == machine_count:
            return
        if tracing is None:
            start_work_times = [i.machines_processing[0] for i in data]
            tracing = {'0': {'delays': [0 for _ in range(len(data))],
                             'times': start_work_times,
                             'sum_delay': 0, 'sum_working': sum(start_work_times)
                             }
                       }
        curr_machine = prev_machine + 1
        delays = []
        for i in range(len(data)):
            delay = max(sum([data[x].machines_processing[prev_machine] for x in range(i)]) -
                        sum([data[x].machines_processing[curr_machine] for x in range(i-1)]) - sum(delays), 0)
            delays.append(delay)
        current_work_times = [delays[i] + data[i].machines_processing[curr_machine] for i in range(len(data))]
        tracing[str(curr_machine)] = {
            'delays': delays, 'times': current_work_times,
            'sum_delay': sum(delays), 'sum_working': sum(current_work_times)
        }
        for i in range(len(data)):
            data[i].machines_processing[curr_machine] += delays[i]
        Johnson.__calc_up_downtime(data, machine_count, prev_machine+1, tracing)
        return tracing


    @staticmethod
    def __find_sum_delay(data):
        return max([reduce(lambda p, c: p+c.machines_processing[0], data[:i]) -
                    reduce(lambda p, c: p+c.machines_processing[0], data[:i-1]) for i in range(len(data))])

    @staticmethod
    def __find_sum_duration(data):
        return sum([i.machines_processing[2] for i in data]) + Johnson.__find_sum_delay(data)

    @staticmethod
    def __opt_cmb(data, prev=None, index=0, opt_path=None):
        if prev is None:
            prev = [0 for _ in range(len(data))]
        if opt_path is None:
            opt_path = dict(duration=math.inf, delay=math.inf, path=None)
        if not len(data):
            delay = Johnson.__find_sum_delay(prev)
            duration = Johnson.__find_sum_duration(prev)
            if opt_path['duration'] > duration:
                opt_path['duration'] = duration
                opt_path['delay'] = delay
                opt_path['path'] = prev
        else:
            for i in range(len(data)):
                prev[index] = str(data[i])
                Johnson.__all_cmb(data[:i] + data[i + 1:], prev, index+1)
        return opt_path
