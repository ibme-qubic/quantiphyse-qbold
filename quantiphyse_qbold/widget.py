"""
qBOLD Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

from PySide import QtGui

from quantiphyse.gui.widgets import QpWidget, Citation, TitleWidget, RunWidget
from quantiphyse.gui.options import OptionBox, DataOption, NumericOption, BoolOption, NumberListOption
from quantiphyse.utils import get_plugins

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class QBoldWidget(QpWidget):
    """
    qBOLD modelling, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="Quantitative BOLD", icon="qp", group="qBOLD-MRI",
                          desc="Bayesian modelling for quantitative BOLD MRI", **kwargs)

    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        try:
            proc = get_plugins("processes", "FabberProcess")[0]
        except:
            proc = None

        if proc is None:
            vbox.addWidget(QtGui.QLabel("Fabber core library not found.\n\n You must install Fabber to use this widget"))
            return

        title = TitleWidget(self, help="fabber-qbold", subtitle="Bayesian modelling for qBOLD-MRI %s" % __version__)
        vbox.addWidget(title)

        cite = Citation(FAB_CITE_TITLE, FAB_CITE_AUTHOR, FAB_CITE_JOURNAL)
        vbox.addWidget(cite)

        self.optbox = OptionBox()
        self.optbox.add("qBOLD Data", DataOption(self.ivm), key="data")
        self.optbox.add("ROI", DataOption(self.ivm, rois=True, data=False), key="mask")
        self.optbox.add("Taus", NumberListOption([0, ]), key="tau")
        self.optbox.add("TE (s)", NumericOption(minval=0, maxval=0.1, default=0.065), key="te")
        self.optbox.add("TR (s)", NumericOption(minval=0, maxval=0.1, default=0.065), key="tr")
        self.optbox.add("TI (s)", NumericOption(minval=0, maxval=0.1, default=0.065), key="ti")

        self.optbox.add("Infer modified T2 rate rather than OEF", BoolOption(default=False), key="inferr2p")
        self.optbox.add("Infer deoxygenated blood volume", BoolOption(default=True), key="inferdbv")
        self.optbox.add("Infer T2 relaxation rate for tissue", BoolOption(default=False), key="inferr2t")
        self.optbox.add("Infer T2 relaxation rate for CSF", BoolOption(default=False), key="inferr2e")
        self.optbox.add("Infer haematocrit fraction", BoolOption(default=False), key="inferhct")
        self.optbox.add("Infer CSF frequency shift", BoolOption(default=False), key="inferdf")
        self.optbox.add("Infer CSF fractional volume", BoolOption(default=False), key="inferlam")
        self.optbox.add("Infer intravascular component", BoolOption(), key="inferintra")

        self.optbox.add("Include CSF signal", BoolOption(), key="inccsf")
        self.optbox.add("Include motional narrowing", BoolOption(), key="motion-narrowing")
        self.optbox.add("Spatial regularization", BoolOption(default=True), key="spatial")
        vbox.addWidget(self.optbox)

        vbox.addWidget(RunWidget(self))

        vbox.addStretch(1)

    def processes(self):
        opts = {
            "model-group" : "qbold",
            "save-mean" : True,
            "save-model-fit" : True,
            "save-model-extras" : True,
            "noise": "white",
            "max-iterations": 20,
            "output-rename" : {
            }
        }
        opts.update(self.optbox.values())
        opts["inferoef"] = not opts["inferr2p"]
        if opts.pop("spatial", False):
            opts["method"] = "spatialvb"
            opts["param-spatial-priors"] = "N+M"

        return {
            "Fabber" : opts
        }
