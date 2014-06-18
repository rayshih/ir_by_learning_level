import os
import pickle

tmp_dir = "./tmp"

class Persist:

  def __init__(self, filename, base_dir=tmp_dir):
    self.filename = filename
    self.base_dir = base_dir

  def dump(self, obj):
    path = self.get_path()
    return pickle.dump(obj, open(path, "wb"))

  def load(self):
    path = self.get_path()
    pickle.dump(open(path, "r"))

  def get_path(self):
    return os.path.join(self.base_dir, self.filename + ".p")

