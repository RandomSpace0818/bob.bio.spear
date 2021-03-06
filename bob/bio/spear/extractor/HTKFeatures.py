#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Elie Khoury <Elie.Khoury@idiap.ch>
# Tue  9 Jun 23:10:43 CEST 2015
#
# Copyright (C) 2012-2015 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Cepstral Features for speaker recognition"""

import numpy
import bob
from .. import utils
import struct

import logging
logger = logging.getLogger("bob.bio.spear")

from bob.bio.base.extractor import Extractor


class HTKFeatures(Extractor):
  """ Extracts the Cepstral features """
  def __init__(
      self,
      features_mask = numpy.arange(0,60),
      normalize_flag = True,
      **kwargs
  ):
      # call base class constructor with its set of parameters
    Extractor.__init__(
        self,
        features_mask = features_mask,
        normalize_flag = normalize_flag,
    )
    # copy parameters
    self.features_mask = features_mask
    self.normalize_flag = normalize_flag


   # TODO: remove redundent code by creating base class
  def normalize_features(self, params):
    normalized_vector = [ [ 0 for i in range(params.shape[1]) ] for j in range(params.shape[0]) ]
    for index in range(params.shape[1]):
      vector = numpy.array([row[index] for row in params])
      n_samples = len(vector)
      norm_vector = utils.normalize_std_array(vector)

      for i in range(n_samples):
        normalized_vector[i][index]=numpy.asscalar(norm_vector[i])
    data = numpy.array(normalized_vector)
    return data


  def HTKReader(self, input_file):
    with open(input_file, 'r') as fid:
        # The resulting array here is float32.  We could explicitly
        # cast it to double, but that will happen further up in the
        # program anyway.
        header = fid.read(12)
        (htk_size, htk_period, vec_size, htk_kind) = struct.unpack('>iihh', header)
        data = numpy.fromfile(fid, dtype='f')
        param = data.reshape((htk_size, vec_size / 4)).byteswap()
    return param

  def __call__(self, data):
    """Read the HTK feature file and (optionally) returns normalized cepstral features for the given VAD labels """
    htk_file = data[0]
    vad_labels = data[1]

    # Read HTK features
    cepstral_features=self.HTKReader(hkt_file)

    features_mask = self.m_config.features_mask
    filtered_features = numpy.ndarray(shape=((vad_labels == 1).sum(),len(features_mask)), dtype=numpy.float64)
    i=0
    cur_i=0

    for row in cepstral_features:
      if vad_labels[i]==1:
        for k in range(len(features_mask)):
          filtered_features[cur_i,k] = row[features_mask[k]]
        cur_i = cur_i + 1
      i = i+1

    if self.m_config.normalizeFeatures:
      normalized_features = self.normalize_features(filtered_features)
    else:
      normalized_features = filtered_features
    if normalized_features.shape[0] == 0:
      logger.warn("No speech found in: %s", input_file)
      # But do not keep it empty!!! This avoids errors in next steps
      normalized_features=numpy.array([numpy.zeros(len(features_mask))])
    return normalized_features
