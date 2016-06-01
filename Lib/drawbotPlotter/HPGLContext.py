from __future__ import absolute_import, division
import os
from drawBot.context.baseContext import BaseContext, Color, GraphicsState
from drawBot.misc import warnings
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen
from robofab.pens.filterPen import _estimateCubicCurveLength, _getCubicPoint


DEBUG = True

def addHPGLContext():
    if DEBUG:
        import drawBot.context
        reload(drawBot.context)
    from drawBot.context import allContexts
    #if DEBUG:
    #    print allContexts
    allContexts.append(HPGLContext)


HPGLPenColors = {
    (255, 255, 255): 0, # white
    (  0,   0,   0): 1, # black
    (255,   0,   0): 2, # red
    (255, 255,   0): 3, # yellow
    (  0, 255,   0): 4, # green
    (  0, 255, 255): 5, # cyan
    (  0,   0, 255): 6, # blue
    (255,   0, 255): 7, # magenta
}




def formatNumber(n, allow_int=False):
    r = int(round(n))
    if n == r:
        if not allow_int:
            return "%0.1f" % n
        return str(r)
    return "%0.3f" % n


def formatPoint(pt, allow_int=False):
    x = formatNumber(pt[0], allow_int)
    y = formatNumber(pt[1], allow_int)
    return (x, y)
        


class HPGLPen(BasePen):
    
    def __init__(self, state=None, rounding=False):
        BasePen.__init__(self, glyphSet=None)
        self._state = state
        self._rounding = rounding
        self._hpgl = []
        self._prev_segment = None
        self._select_pen()
        
        self.approximateSegmentLength = 10
        self.currentPt = None
    
    def _select_pen(self):
        if self._state.strokeColor is not None:
            self._hpgl.append("SP%i;" % self._state.strokeColor.penColor())
        else:
            self._hpgl.append("SP;")
    
    def _pen_width(self):
        i = int(round(value * 300 / 72))
        if i > 10:
            i = 10
            max_pt = (i + 0.4 ) * 72 / 300
            warnings.warn("Stroke widths > %0.2f are not supported in the HPGL context." % max_pt)
        self._hpglData.write(["PW%i;" % i])
    
    def _get_transformed_pt(self, (x, y)):
        if self._state.transformMatrix is not None:
            (x, y) = self._state.transformMatrix.transformPoint((x, y))
        if self._rounding:
            return (int(round(x)), int(round(y)))
        else:
            return (x, y)
    
    def _get_transformed_pts(self, *pts):
        return [self._get_transformed_pt(pt) for pt in pts]
    
    
    # Pen basics
    
    def _moveTo(self, pt):
        self._prev_move = pt
        self.currentPt = pt
        pt = self._get_transformed_pt(pt)
        self._hpgl.append("PU%s,%s" % formatPoint(pt, self._rounding))
        self._prev_segment = "move"

    def _lineTo(self, pt):
        self.currentPt = pt
        if self._prev_segment not in ["line", "curve"]:
            self._hpgl.append(";PD")
        else:
            self._hpgl.append(",")
        pt = self._get_transformed_pt(pt)
        self._hpgl.append("%s,%s" % formatPoint(pt, self._rounding))
        self._prev_segment = "line"

    def _curveToOne(self, bcp1, bcp2, pt):
        orig = self.currentPt
        orig_pt = pt
        
        # Shamelessly lifted from robofab.pens.filterPen.FlattenPen
        
        est = _estimateCubicCurveLength(self.currentPt, bcp1, bcp2, pt)/self.approximateSegmentLength
        maxSteps = int(round(est))
        falseCurve = (bcp1==self.currentPt) and (bcp2==pt)
        if maxSteps < 1 or falseCurve:
            self.lineTo(pt)
            self._prev_segment = "line"
            return
        step = 1.0/maxSteps
        factors = range(0, maxSteps+1)
        for i in factors[1:]:
            p = _getCubicPoint(i*step, orig, bcp1, bcp2, pt)
            self.lineTo(p)
        
        self.currentPt = orig_pt
        self._prev_segment = "line"

    def _closePath(self):
        if self._prev_segment not in ["line", "curve"]:
            self._hpgl.append(";PD")
            self._hpgl.append("%s,%s" % formatPoint(pt, self._rounding))
            self._hpgl.append(";PU")
            self._hpgl.append(";\n")
        else:
            self._hpgl.append(",")
            pt = self._get_transformed_pt(self._prev_move)
            self._hpgl.append("%s,%s" % formatPoint(pt, self._rounding))
            self._hpgl.append(";PU")
            self._hpgl.append(";\n")
        self._prev_segment = "close"
    
    def _endPath(self):
        self._hpgl.append(";PU")
        self._hpgl.append(";\n")
        self._prev_segment = "end"
    
    
    # Convenience methods
    # FIXME: transformation on relative coordinates (w, h) ...
    
    def oval(self, x, y, w, h):
        w /= 2
        (x, y), (w, h) = self._get_transformed_pts((x, y), (w, h))
        self._hpgl.extend([
            "PU%s,%s;" % (x, y),
            "CI%s;" % w,
            "\n"
        ])
    
    def rect(self, x, y, w, h):
        (x, y), (w, h) = self._get_transformed_pts((x, y), (w, h))
        self._hpgl.extend([
            "PU%s,%s;" % (x, y),
            "ER%s,%s;" % (w, h),
            "\n"
        ])
    
    @property
    def hpgl(self):
        return self._hpgl



class HPGLFile(object):

    optimize = False

    def __init__(self):
        self._hpgldata = []

    def write(self, value):
        if DEBUG:
            print "    HPGLFile.write()", value
        self._hpgldata.extend(value)

    def writeToFile(self, path):
        if DEBUG:
            print "HPGLFile.writeToFile()", path
        data = self.read()
        f = open(path, "w")
        f.write(data)
        f.close()

    def read(self):
        return "".join(self._hpgldata)

    def close(self):
        pass



class HPGLColor(Color):

    def penColor(self):
        c = self.getNSObject()
        if c:
            if c.numberOfComponents() == 2:
                r = g = b = 1
            else:
                r = int(255*round(c.redComponent()))
                g = int(255*round(c.greenComponent()))
                b = int(255*round(c.blueComponent()))
            a = int(round(c.alphaComponent()))
            if a == 0:
                r = g = b = 0
            return HPGLPenColors.get((r, g, b), None)
        return None



class HPGLGraphicsState(GraphicsState):

    _colorClass = HPGLColor

    def __init__(self):
        super(HPGLGraphicsState, self).__init__()
        self.transformMatrix = Transform(1, 0, 0, 1, 0, 0)
        self.currentPen = None

    def copy(self):
        new = super(HPGLGraphicsState, self).copy()
        new.transformMatrix = Transform(*self.transformMatrix[:])
        return new



class HPGLContext(BaseContext):
    
    _graphicsStateClass = HPGLGraphicsState
    _colorClass = HPGLColor
    
    _hpglFileClass = HPGLFile
    
    fileExtensions = ["hpgl"]
    
        
    def __init__(self):
        if DEBUG:
            print "HPGLContext.__init__()"
        super(HPGLContext, self).__init__()
        self._pages = []
        self._hpgl_base_unit = 1/1016 # inch
        self._safety_margin = 0.9 # printable area percentage
        self._rounding = True
        
    
    # HPGL stuff
    
    def _set_scaling_info(self):
        """IP = Scaling Point x1, y1, x2, y2
        
        The maximum coordinates are plotter-specific and given in HPGL units (1/1016 inch).
        Make sure not to exceed the plot area, otherwise the IP instruction will be ignored.
        For Bernd's plotter:
           max x = 16158 units ~ 403,95 mm or 16 mm less than A3
           max y = 11040 units ~ 276,00 mm or 21 mm less than A3
           
           16792 (A3) - 16158 = 814 (96%)
           11882 (A3) - 11040 = 842 (92%)
           
        """
        ip_x2 = int(round(self.width  / 72 / self._hpgl_base_unit))
        ip_y2 = int(round(self.height / 72 / self._hpgl_base_unit))
        
        # Assume a safety margin of 90% of the given weight/height
        
        self.ip_x2 = int(round(ip_x2 * self._safety_margin))
        self.ip_y2 = int(round(ip_y2 * self._safety_margin))
        
        # SC = Scale xmin, ymin, xmax, ymax
        self.sc_x_max = self.width  * self._safety_margin
        self.sc_y_max = self.height * self._safety_margin
    
    
    def _get_init_sequence(self):
        self._set_scaling_info()
        seq = [
            # IN = Initialize
            "IN;",              
            # IP = Scaling Point x1, y1, x2, y2
            "IP%s,%s,%s,%s;" % (0, 0, self.ip_x2, self.ip_y2),
            # SC = Scale 
            "SC%s,%s,%s,%s;" % (0, 0, self.sc_x_max, self.sc_y_max),
            # the rest of the init sequence
            "PU;",   # PU = Pen Up
            #"SP1;",  # SP1 = Select Pen 1
            "LT;",   # LT = Line Type solid
            "\n",
        ]
        
        # After the scaling is set, coordinates must be floats
        self._rounding = False
        
        return seq
    
    
    def _get_end_sequence(self):
        seq = [
            #"PU;",    # PU = Pen Up
            "SP;",    # Put down the pen
            # "EC;",  # EC = Perforate paper
            # "PG1;", # PG = Page Feed
            # "EC1;", # EC = ?
            "PA0,0;", # Move head to 0, 0
            #"OE;",    # OE = Output Error
            "\n",
        ]
        return seq
    
    
    # Context-specific stuff
    
    def _reset(self):
        self._state.transformMatrix = Transform(1, 0, 0, 1, 0, 0)
        self._rounding = True
        self._state.pen = False
    
    
    def _newPage(self, width, height):
        if DEBUG:
            print "HPGLContext._newPage()"
        if hasattr(self, "_hpglData"):
            self._hpglData.write(self._get_end_sequence())
            self._pages.append(self._hpglData)
        self.reset()
        self.size(width, height)
        self._hpglData = self._hpglFileClass()
        self._hpglData.write(self._get_init_sequence())
    
    
    def _drawPath(self):
        if DEBUG:
            print "HPGLContext._drawPath()"
        if self._state.path:
            hp = HPGLPen(self._state, self._rounding)
            self._state.path.drawToPen(hp)
            self._hpglData.write(hp.hpgl)
    
    
    def _clipPath(self):
        pass
        # TODO
        # Clip path can be any path, but HPGL only supports a rect
    
    
    def _saveImage(self, path, multipage):
        if DEBUG:
            print "HPGLContext._saveImage()"
        if multipage is None:
            multipage = False
        self._hpglData.write(self._get_end_sequence())
        self._pages.append(self._hpglData)
        fileName, fileExt = os.path.splitext(path)
        firstPage = 0
        pageCount = len(self._pages)
        if DEBUG:
            print "    Pages:", pageCount
        pathAdd = "_1"
        if not multipage:
            firstPage = pageCount - 1
            pathAdd = ""
        for index in range(firstPage, pageCount):
            page = self._pages[index]
            hpglPath = fileName + pathAdd + fileExt
            page.writeToFile(hpglPath)
            pathAdd = "_%s" % (index + 2)
    
    
    def _transform(self, transform):
        self._state.transformMatrix = self._state.transformMatrix.transform(transform)
    
    
    # Shortcut methods
    # These would be handled by the general path drawing otherwise
    
    """
    def oval(self, x, y, w, h):
        if w == h:
            hp = HPGLPen(self._state)
            hp.oval(x, y, w, h)
            self._hpglData.write(hp.hpgl)
        else:
            super(HPGLContext, self).oval(self, x, y, w, h)
    
    
    def rect(self, x, y, w, h):
        if self._state.transformMatrix is None:
            hp = HPGLPen(self._state)
            hp.rect(x, y, w, h)
            self._hpglData.write(hp.hpgl)
        else:
            super(HPGLContext, self).rect(x, y, w, h)
    """
