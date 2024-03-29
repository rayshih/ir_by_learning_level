import os
import pickle
import gzip, cPickle

tmp_dir = "./tmp"

class Persist:

  def __init__(self, filename, base_dir=tmp_dir):
    self.filename = filename
    self.base_dir = base_dir

  def dump(self, obj):
    path = self.get_path()
    #return pickle.dump(obj, open(path, "wb"))
    pkl = cPickle.dumps(obj, protocol = cPickle.HIGHEST_PROTOCOL)
    with gzip.open(path,'wb') as fp:
        fp.write(pkl)

  def load(self):
    path = self.get_path()
    #return pickle.load(open(path, "rb"))
    with gzip.open(path,'rb') as fp:
        return cPickle.load(fp)

  def get_path(self):
    return os.path.join(self.base_dir, self.filename + ".p")

