import numpy
import scipy.io.wavfile
import bob.io.base

from bob.bio.base.preprocessor import Preprocessor


class Base (Preprocessor):
  """Performs color space adaptations and data type corrections for the given image"""

  def __init__(self, **kwargs):
    Preprocessor.__init__(self, **kwargs)
    # Each class needs to have a constructor taking
    # all the parameters that are required for the preprocessing as arguments
    self._kwargs = kwargs
    pass

  def write_data(self, data, data_file, compression=0):
    """Writes the given *preprocessed* data to a file with the given name.
    """
    f = bob.io.base.HDF5File(data_file, 'w')
#    f.set("rate", data[0], compression=compression) # sss #
#    f.set("data", data[1].astype('int16'), compression=compression)
    f.set("labels", data[2].astype('int8'), compression=compression)


  def read_data(self, data_file):
    f= bob.io.base.HDF5File(data_file)
#    rate    = f.read("rate") # sss #
#    data   = f.read("data").astype('float64')
    labels = f.read("labels")
    return labels #rate, data, labels # sss #

