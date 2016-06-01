from __future__ import absolute_import, division

"""
Simple class to draw an HPGL file in DrawBot.
"""

from drawbotPlotter.HPGLContext import HPGLPenColors
from drawBot.drawBotDrawingTools import _drawBotDrawingTool
_drawBotDrawingTool._addToNamespace(globals())

from os.path import expanduser



class HPGLDraw(object):
    def __init__(self, path, width, height):
        self.debug = False
        f = open(expanduser(path), "rb")
        self.data = f.read()
        f.close()
        self.width = width
        self.height = height
        self.parse()
        self.draw()
    
    def parse(self):
        cmd_list = [c.strip() for c in self.data.split(";") if not c.strip() == ""]
        self.commands = []
        for c in cmd_list:
            code = c[:2]
            if c[2:]:
                params = [float(p) for p in c[2:].split(",")]
            else:
                params = []
            self.commands.append((code, params))
            
    
    def draw(self):
        have_path = False
        for c, p in self.commands:
            if c == "IN":
                newPage(self.width, self.height)
                fill(None)
                save()
                fill(1, 1, 0, 0.1)
                rect(0, 0, self.width, self.height)
                strokeWidth(1)
                stroke(0)
                restore()
            elif c == "PU":
                if self.debug:
                    print c, p
                if have_path:
                    if len(p) < 2:
                        if self.debug:
                            print "    endPath"
                        path.endPath()
                        drawPath(path)
                        have_path = False
                    else:
                        if self.debug:
                            print "    endPath"
                        path.endPath()
                        drawPath(path)
                        if self.debug:
                            print "    moveTo", p[-2], p[-1]
                        path.moveTo((p[-2], p[-1]))
                else:
                    if len(p) > 1:
                        if self.debug:
                            print "    moveTo", p[0], p[1]
                        path = BezierPath()
                        path.moveTo((p[-2], p[-1]))
                        have_path = True
                    else:
                        if self.debug:
                            print "    NO-OP"
                        have_path = False
            elif c == "PD":
                if p:
                    pt = [None, None]
                    for i, coord in enumerate(p):
                        pt[i%2] = coord
                        if i%2 == 1:
                            if self.debug:
                                print "    lineTo", pt[0], pt[1]
                            path.lineTo((pt[0], pt[1]))
            #elif c == "SC":
            #    if len(p) == 4:
            #        newPage(p[2], p[3])
            #        fill(None)
            #        save()
            #        fill(1, 1, 0, 0.1)
            #        rect(0, 0, p[2], p[3])
            #        strokeWidth(1)
            #        stroke(0)
            #        restore()
            elif c == "SP":
                if self.debug:
                    print c, p
                if have_path:
                    if self.debug:
                        print "    endPath (due to SP)"
                    path.endPath()
                    drawPath(path)
                    have_path = False
                if len(p) == 1:
                    pen_index = int(p[0])
                    for c, i in HPGLPenColors.items():
                        if i == pen_index:
                            stroke(*c)
                            if self.debug:
                                print "    stroke", c
                else:
                    stroke(None)
                    if self.debug:
                        print "    stroke", None
