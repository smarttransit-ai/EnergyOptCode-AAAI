# -------------------------------------------------------------------------------- #
#                    PARALLEL PROCESSING USING MULTIPROCESSING                     #
# -------------------------------------------------------------------------------- #
import itertools
import time
from multiprocessing import Manager, Process, cpu_count

process_count = int(0.8 * cpu_count())


class CustomPyParallel:
    def __init__(self, limit):
        self._limit = limit
        self._no_of_process = min(process_count, limit)

    def _add_proc(self, func, args=None):
        pass

    def run(self):
        pass


class SharedList:
    def __init__(self, limit):
        self.manager = Manager()
        self.tasks = self.manager.Queue()
        self.results = self.manager.Queue()
        self.outputs = []
        self.limit = limit
        self.no_of_process = min(process_count, limit)

    def setup(self):
        for i in range(self.limit):
            self.tasks.put(0)
        time.sleep(0.1)
        for i in range(self.no_of_process):
            self.tasks.put(-1)
        time.sleep(0.1)

    def append(self, new_value):
        task_val = self.tasks.get()
        if task_val < 0:
            self.results.put(-1)
            success = False
        else:
            self.results.put(new_value)
            success = True
        return success

    def list(self):
        num_finished_processes = 0
        while True:
            new_result = self.results.get()
            if new_result == -1:
                num_finished_processes += 1
                if num_finished_processes == self.no_of_process:
                    break
            else:
                self.outputs.append(new_result)
        return self.outputs


class KeySharedList(SharedList):
    def __init__(self, keys):
        super(KeySharedList, self).__init__(len(keys))
        self.received_keys = keys

    def append(self, value, key=None):
        if key in self.received_keys:
            self.received_keys.remove(key)
            self.results.put(value)
            self.results.put(-1)
            success = True
        else:
            success = False
        return success

    def list(self):
        num_finished_processes = 0
        while True:
            new_result = self.results.get()
            if new_result == -1:
                num_finished_processes += 1
                if num_finished_processes == self.limit:
                    break
            else:
                self.outputs.append(new_result)
        return self.outputs


class CustomMultiProcessing:
    def __init__(self):
        self.__processes = []

    def add_process(self, func, args):
        process = Process(target=func, args=args)
        self.__processes.append(process)

    def start(self):
        for __process in self.__processes:
            __process.start()

    def join(self):
        for __process in self.__processes:
            __process.join()


class CMPSystem(CustomPyParallel):
    def __init__(self, limit, store_data=True):
        super(CMPSystem, self).__init__(limit)
        self._multi_proc = CustomMultiProcessing()
        self._store_data = store_data
        self._shared_list = None
        self._setup()

    def _setup(self):
        self._shared_list = SharedList(self._limit)

    def _add_proc(self, func, args=None):
        for i in range(self._no_of_process):
            process_name = 'process_%i' % i
            if self._store_data:
                updated_args = (process_name, self._shared_list)
            else:
                updated_args = (process_name,)
            if args is not None:
                updated_args += args
            self._multi_proc.add_process(func=func, args=updated_args)

    def add_proc(self, func, args=None):
        return self._add_proc(func, args)

    def run(self):
        self._multi_proc.start()
        self._shared_list.setup()
        result = self._shared_list.list()
        self._multi_proc.join()
        return result


class MultiCMPPairOverFlow(Exception):
    def __init__(self, *args):
        super(MultiCMPPairOverFlow, self).__init__(args)


# This customizable functionality, you can modify the output by default,
# add also for small ranges you can use full access. It is safe as long as
# total process not exceeds the amount
class MultiCMPSys(CMPSystem):
    def __init__(self, row_values, col_values, data_store=True, forced=True):
        self._contents = [(r, c) for (r, c) in itertools.product(row_values, col_values)]
        try:
            self._row_values = [r.__str__() for r in row_values]
            self._col_values = [c.__str__() for c in col_values]
        except AttributeError:
            self._row_values = [r for r in row_values]
            self._col_values = [c for c in col_values]
        if forced:
            super(MultiCMPSys, self).__init__(min(process_count, len(self._contents)), data_store)
        else:
            super(MultiCMPSys, self).__init__(len(self._contents), True)

    def _setup(self):
        if len(self._contents) > self._no_of_process:
            raise MultiCMPPairOverFlow("contents with higher dimension are not allowed")
            # added this error to avoid failing
        self._shared_list = KeySharedList(self._contents)

    def _add_proc(self, func, args=None):
        for i, row in enumerate(self._contents):
            process_name = 'process_%i' % i
            if self._store_data:
                updated_args = (process_name, self._shared_list) + row
            else:
                updated_args = (process_name,) + row
            if args is not None:
                updated_args += args
            self._multi_proc.add_process(func=func, args=updated_args)
