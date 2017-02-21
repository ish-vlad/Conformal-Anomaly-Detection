from nab.detectors.base import AnomalyDetector
import numpy as np


class LofDetector(AnomalyDetector):

    def __init__(self, *args, **kwargs):
        super(LofDetector, self).__init__(*args, **kwargs)
        # Hyperparams
        self.k = 2
        self.dim = 2

        # Algorithm attributes
        self.buf = []
        self.training = []
        self.record_count = 0
        self.rang = self.inputMax - self.inputMin

        # Mahalanobis attributes
        self.sigma = np.diag(np.ones(self.dim))
        self.sigma_inv = np.diag(np.ones(self.dim))
        self.mean = -1

    def lof(self, item, array):
        if not isinstance(array, np.ndarray):
            array = np.array(array)

        mean_dist, neighbours = self.get_NN_dist(np.array(item), array, return_nn=True)

        lrd = min(1. / mean_dist, self.rang * 1e+5)
        lrds = [min(1. / self.get_NN_dist(np.array(nn), array), self.rang * 1e+5) for nn in array[neighbours]]
        return np.sum(lrds) / self.k / lrd

    def handleRecord(self, inputData):
        """
        inputRow = [inputData["timestamp"], inputData["value"]]
        """
        self.buf.append(inputData["value"])

        if len(self.buf) < self.dim:
            return [0.0]
        else:
            new_item = self.buf[-self.dim:]
            self.record_count += 1
            if self.record_count < self.probationaryPeriod - self.dim:
                self.training.append(new_item)
                return [0.0]
            else:
                self.training.append(new_item)
                self.update_sigma()

                return [max(0,1-1./self.lof(np.array(new_item), np.array(self.training)))]
