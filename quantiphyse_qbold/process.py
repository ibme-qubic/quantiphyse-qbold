"""
qBOLD Quantiphyse plugin

Custom Fabber process with postprocessing step

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

import numpy as np

from quantiphyse.processes import Process

class QBoldCalculateOEF(Process):
    """
    Calculate CBF from R2P / DBV output
    """
    
    PROCESS_NAME = "QBoldCalculateOEF"
    
    def __init__(self, ivm, **kwargs):
        Process.__init__(self, ivm, **kwargs)

    def run(self, options):
        suffix = options.pop('output-suffix', '')
        hct = options.pop("hct", 0.4)
        r2p_name = options.pop("r2p", "r2p%s" % suffix)
        dbv_name = options.pop("dbv", "dbv%s" % suffix)

        r2p = self.ivm.data[r2p_name]
        dbv = self.ivm.data[dbv_name]

        # See https://quantiphyse.readthedocs.io/en/latest/qbold/tutorial.html
        # for details of calculation
        oef = (r2p.raw() * 0.00113)/(hct * dbv.raw())
        self.ivm.add(oef, name="oef%s" % suffix, grid=dbv.grid)
