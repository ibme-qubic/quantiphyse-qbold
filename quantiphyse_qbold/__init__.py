"""
qBOLD Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
from .widget import QBoldWidget
from .process import QBoldCalculateOEF
QP_MANIFEST = {
    "widgets" : [QBoldWidget],
    "processes" : [QBoldCalculateOEF],
}
