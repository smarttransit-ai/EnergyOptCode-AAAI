import pickle

from common.util.common_util import create_dir


def dump_obj(obj, file_name):
    create_dir(file_name)
    dump_file = open(file_name, "wb")
    pickle.dump(obj, dump_file)
    dump_file.close()


def load_obj(file_name):
    dump_file = open(file_name, "rb")
    obj = pickle.load(dump_file)
    dump_file.close()
    return obj
