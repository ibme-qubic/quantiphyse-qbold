"""
qBOLD Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""

from __future__ import division, unicode_literals, absolute_import, print_function

try:
    from PySide import QtGui, QtCore, QtGui as QtWidgets
except ImportError:
    from PySide2 import QtGui, QtCore, QtWidgets

from quantiphyse.gui.widgets import QpWidget, Citation, TitleWidget, RunWidget
from quantiphyse.gui.options import OptionBox, DataOption, NumericOption, BoolOption, NumberListOption

from ._version import __version__

FAB_CITE_TITLE = "Variational Bayesian inference for a non-linear forward model"
FAB_CITE_AUTHOR = "Chappell MA, Groves AR, Whitcher B, Woolrich MW."
FAB_CITE_JOURNAL = "IEEE Transactions on Signal Processing 57(1):223-236, 2009."

class QBoldWidget(QpWidget):
    """
    qBOLD modelling, using the Fabber process
    """
    def __init__(self, **kwargs):
        QpWidget.__init__(self, name="Quantitative BOLD", icon="qbold", group="BOLD-MRI",
                          desc="Bayesian modelling for quantitative BOLD MRI", **kwargs)

    def init_ui(self):
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        title = TitleWidget(self, help="fabber-qbold", subtitle="Bayesian modelling for qBOLD-MRI %s" % __version__)
        vbox.addWidget(title)

        cite = Citation(FAB_CITE_TITLE, FAB_CITE_AUTHOR, FAB_CITE_JOURNAL)
        vbox.addWidget(cite)

        self._optbox = OptionBox()
        self._optbox.add("<b>Data</b>")
        self._optbox.add("qBOLD Data", DataOption(self.ivm), key="data")
        self._optbox.add("ROI", DataOption(self.ivm, rois=True, data=False), key="roi")
        self._optbox.add("Taus (s)", NumberListOption([0, ]), key="tau")
        self._optbox.add("TE (s)", NumericOption(minval=0, maxval=0.1, default=0.065), key="te")
        self._optbox.add("TR (s)", NumericOption(minval=0, maxval=5, default=3.0), key="tr")
        self._optbox.add("TI (s)", NumericOption(minval=0, maxval=5, default=1.2), key="ti")

        self._optbox.add("<b>Model options</b>")
        self._optbox.add("Infer modified T2 rate rather than OEF", BoolOption(default=True), key="inferr2p")
        self._optbox.add("Infer deoxygenated blood volume", BoolOption(default=True), key="inferdbv")
        # We probably don't want to expose these options
        #self._optbox.add("Infer T2 relaxation rate for tissue", BoolOption(default=False), key="inferr2t")
        #self._optbox.add("Infer T2 relaxation rate for CSF", BoolOption(default=False), key="inferr2e")
        #self._optbox.add("Infer haematocrit fraction", BoolOption(default=False), key="inferhct")

        self._optbox.add("Include CSF compartment", BoolOption(default=False), key="inccsf")
        self._optbox.add("Infer CSF frequency shift", BoolOption(default=False), key="inferdf", visible=False)
        self._optbox.add("Infer CSF fractional volume", BoolOption(default=False), key="inferlam", visible=False)

        self._optbox.add("Include intravascular compartment", BoolOption(default=False), key="incintra")
        self._optbox.add("Use motional narrowing model", BoolOption(default=False), 
                         key="motion-narrowing", visible=False)

        self._optbox.add("<b>Model fitting options</b>")
        self._optbox.add("Spatial regularization", BoolOption(default=True), key="spatial")
        self._optbox.sig_changed.connect(self._options_changed)
        vbox.addWidget(self._optbox)

        vbox.addWidget(RunWidget(self))
        vbox.addStretch(1)
        self._options_changed()

    def _options_changed(self):
        inccsf = self._optbox.option("inccsf").value
        self._optbox.set_visible("inferdf", inccsf)
        self._optbox.set_visible("inferlam", inccsf)
        incintra = self._optbox.option("incintra").value
        self._optbox.set_visible("motion-narrowing", incintra)
        inferr2p = self._optbox.option("inferr2p").value
        self._optbox.set_visible("inferdbv", inferr2p)

    def processes(self):
        opts = {
            "model-group" : "qbold",
            "model" : "qboldR2p",
            "save-mean" : True,
            "save-model-fit" : True,
            "save-model-extras" : True,
            "noise" : "white",
            "max-iterations" : 20,
            "infersig0" : True,
            "output-rename" : {
            }
        }
        opts.update(self._optbox.values())
        opts["inferoef"] = not opts["inferr2p"]
        if opts.pop("spatial", False):
            # In spatial mode use sig0 as regularization parameter
            opts["method"] = "spatialvb"
            opts["param-spatial-priors"] = "MN+"

        # FIXME couldn't the Fabber API handle this?
        taus = opts.pop("tau")
        for idx, tau in enumerate(taus):
            opts["tau%i" % (idx+1)] = tau

        self.debug("%s", opts)
        return {
            "Fabber" : opts
        }
