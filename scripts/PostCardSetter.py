from __future__ import absolute_import
from fontTools.agl import UV2AGL
import sys
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7")
import chiplotle
from defcon import Font
from drawBot.drawBotDrawingTools import _drawBotDrawingTool
from fontTools.pens.cocoaPen import CocoaPen
from drawBot.drawBotDrawingTools import _drawBotDrawingTool
import subprocess
from os.path import expanduser
import os
from time import mktime, gmtime
from vanilla import *
from drawBot.context import allContexts

addHPGLContext()

# Set min/max curve splitting values in HPGL context
hc = allContexts[-1]
hc.min_segment_units = 20
hc.max_curve_steps = 50


DEBUG = True


def now(): 
   return mktime(gmtime()) 


from re import compile, search

class jkKernInfo(object):
    
    def __init__(self, font):
        self.font = font
        self.group_name_pattern = compile("^@MMK_*")
        self.group_name_l_pattern = compile("^@MMK_L_*")
        self.group_name_r_pattern = compile("^@MMK_R_*")
        self._analyze_kerning()
    
    def is_kerning_group(self, name, side=None):
        # Test if supplied name is a kerning group name
        if side is None:
            return self.group_name_pattern.search(name)
        elif side == "l":
            return self.group_name_l_pattern.search(name)
        elif side == "r":
            return self.group_name_r_pattern.search(name)

        return False

    
    def _analyze_kerning(self):
        self.group_info = {
            "l": {},
            "r": {},
        }
        if self.font is not None:
            self.kerning = self.font.kerning
            for group_name, group_content in self.font.groups.items():
                if self.is_kerning_group(group_name, "l"):
                    for glyph_name in group_content:
                        self.group_info["l"][glyph_name] = group_name
                if self.is_kerning_group(group_name, "r"):
                    for glyph_name in group_content:
                        self.group_info["r"][glyph_name] = group_name
    
    def get_group_for_glyph(self, glyph_name, side):
        group_name = self.group_info[side].get(glyph_name, None)
        return group_name
    
    def getKernValue(self, left, right):
        left_group = self.get_group_for_glyph(left, "l")
        right_group = self.get_group_for_glyph(right, "r")
        if self.font is None:
            return 0
        pair_value = self.kerning.get((left, right), None)
        if pair_value is not None:
            return pair_value
        lg_value = self.kerning.get((left_group, right), None)
        if lg_value is not None:
            return lg_value
        rg_value = self.kerning.get((left, right_group), None)
        if rg_value is not None:
            return rg_value
        group_value = self.kerning.get((left_group, right_group), None)
        if group_value is None:
            group_value = 0
        return group_value


def drawGlyph(glyph):
    pen = CocoaPen(glyph.getParent())
    glyph.draw(pen)
    path = pen.path
    _drawBotDrawingTool.drawPath(path)

_drawBotDrawingTool.drawGlyph = drawGlyph

def plot(hpgl_path):
    #Drawing limits: (left 0; bottom 0; right 16158; top 11040)
    #format = 'hpgl'
    format = 'plot-hpgl'
    abs_path = expanduser(hpgl_path)
    saveImage(abs_path)
    # Send to plotter
    if DEBUG:
        HPGLDraw(abs_path, width(), height())
    else:
        plotter = chiplotle.instantiate_plotters( )[0]
        plotter.write_file(abs_path)

# Parallel pen sizes in pt
pp_sizes = {
    0: 14.173, # 5.0 mm
    1: 10.772, # 3.8 mm
    2: 6.803,  # 2.4 mm
    3: 4.252,  # 1.5 mm
}

# Font Choice
fonts_list = {
    0: Font (expanduser("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Mark_CenterLine_03.ufo")),
    1: Font (expanduser("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/HertzTypewriterLine-Light.ufo")),
    2: Font (expanduser("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_outline_01.ufo")),
    3: Font (expanduser("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/manVSmachine7.ufo")),    
   }

def getGlyphNamesFromString(my_string):
    #my_string = my_string.decode("utf-8")
    glyphNames = []
    for char in my_string:
        if char == "\n":
            glyphNames.append(r"\n")
        else:
            uni = ord(char)
            glyphName = UV2AGL.get(uni)
            if glyphName:
                glyphNames.append(glyphName)
    return glyphNames

class FontProofer(object):
    
    def getPickedFont():
        print "Picked Font"
        print self.font
    
    def __init__(self, font=None, font_index=0, caps_lock=False, linespace=0.7, marginsupdown = 20, marginsside = 20, nib_simulate=False, nib_width_index=0, nib_angle=30, Color_Nib=False, send_to_plotter=False):       
        
        self.linespace = linespace
        self.font_index = font_index
        self.set_font(font)    
        
        #for 2000 UPM Fonts
        if font_index == 0:
            self.upm = 2000
            self.desc = -500
            self.x_height = 1000
            self.cap_height = 1400
            self.asc = 1500
            self.angle = 0
            
        self.mark_fill = False
        self.mark_composites = False
        
        # A6 Format
        hpglscale = 1.3752
        self.width = 842/2 *hpglscale
        self.height = 595/2 *hpglscale
        
        self.margins = {
            "top": marginsupdown,
            "bottom": marginsupdown,
            "left": marginsside,
            "right": marginsside,
        
        }
        self.breite = 842/2 *hpglscale - marginsside * 1.5*hpglscale
        self.scale = 1 
        
        self.nib_simulate = nib_simulate
        
        if nib_width_index in pp_sizes:
            self.nib_width_pt = pp_sizes[nib_width_index]
        else:
            self.nib_width_pt = 14.173 * hpglscale
        self.nib_width = self.nib_width_pt / self.scale *hpglscale
        
        self.nib_angle = radians(nib_angle)
                   
        if font_index in fonts_list:
             print "Selected font: ", font_index + 1
             self.set_font(fonts_list[font_index])
        print "\nNib Simulation Parameters","\nNib Width:     ", (round((self.nib_width / 4),1))+0.1,"mm", "\nNib Angle:     ",(round((nib_angle),1)),"°","\n"
        
        self.x_pad = 10
        self.y_pad = 24
        print "Leading:       ", round(linespace*(1/0.7), 2),"\nVertical Shift:", round((marginsupdown-20)*-1,1),"\nScale-Factor:  ", round(((marginsside-260)*-1)/2.4, 1), "%","\n"
        self.Color_Nib = Color_Nib
        self.send_to_plotter = send_to_plotter
        
    
    
    
    def set_font(self, font=None):
        self.font = font
        if self.font is not None:
            self.kerning = jkKernInfo(self.font)
            self.upm = self.font.info.unitsPerEm
            self.desc = self.font.info.descender
            self.x_height = self.font.info.xHeight
            self.cap_height = self.font.info.capHeight
            self.asc = self.font.info.ascender
            self.angle = self.font.info.italicAngle
        
        else:
            self.kerning = jkKernInfo(self.font)
            self.upm = 1000
            self.desc = -250
            self.x_height = 500
            self.cap_height = 700
            self.asc = 750
            self.angle = 0
    
    def new_page(self):
        newPage(self.width, self.height)
        translate(self.margins["left"], self.height - self.margins["top"] - self.asc * self.scale)
    
    def _drawGlyph(self, glyph):
        save()
        scale(self.scale)
        
        fill(None)
        lineJoin("round")
        miterLimit(1)
        strokeWidth(1.6/self.scale)
        stroke(0, 0, 0, 1)
        drawGlyph(glyph)
        if self.nib_simulate:
            if self.Color_Nib:
                stroke(1, 0, 0, 1)
            save()
            translate((self.nib_width * -0.5 * cos(self.nib_angle))*(1/self.scale), self.nib_width * -0.5 * sin(self.nib_angle)*(1/self.scale))
            drawGlyph(glyph)
            restore()
            save()
            translate((self.nib_width * 0.5 * cos(self.nib_angle))*(1/self.scale), self.nib_width * 0.5 * sin(self.nib_angle)*(1/self.scale))
            drawGlyph(glyph)
            restore()
        restore()
    
    def _drawMetrics(self, glyph):
        save()
        stroke(0.7)
        w = glyph.width
        if self.mark_fill:
            if glyph.mark is not None:
                save()
                fill(glyph.mark[0], glyph.mark[1], glyph.mark[2], 0.5)
                rect(0, self.desc, w, abs(self.desc) + self.asc)
                restore()
        
        line((0, self.desc), (0, self.asc))
        if w != 0:
            line((0, self.desc), (w, 0 + self.desc))
            line((0, 0), (w, 0))
            line((0, self.x_height), (w, 0 + self.x_height))
            line((0, self.cap_height), (w, 0 + self.cap_height))
            line((0, self.asc), (w, 0 + self.asc))
            line((w, self.desc), (w, self.asc))

        restore()
        
    
    def getGlyphnameList(self, my_text):
        
        return [ord(n) for n in my_text]
        
    def getTextWidth(self, my_text):
        lines = my_text.splitlines()
        maxWidth = 0
        self.linelength = []
        
        for line in lines:
            LineWidth = self.getLineWidth(line.strip())
            self.linelength.append(LineWidth) 
        
            if LineWidth > maxWidth:
                maxWidth = LineWidth
        
        count = 0
        for linelength in self.linelength:
            print "Line %s is %s ✕ line %s" %(self.linelength.index(linelength)+1,  round(maxWidth/linelength,2), self.linelength.index(maxWidth)+1) 
        print ""
        return maxWidth 
            
        
    def getLineWidth(self, my_text):
        totalwidth = 0
        my_list = getGlyphNamesFromString(my_text)
        for i, gn in enumerate(my_list):
            if not gn in self.font:
                print "Missing glyph:", gn
            else:
                glyph = self.font[gn]
                xadv = glyph.width
                if i < len(my_list)-1:
                    totalwidth += xadv + self.kerning.getKernValue(gn,my_list[i+1])
                else:
                    totalwidth += xadv
        return totalwidth    
            
    def setText(self, my_text):
        lines = my_text.splitlines()
        my_list = getGlyphNamesFromString(my_text)        
        
        if self.font is None:
            print "Pick a font"
            return None
            
        self.getTextWidth(my_text)
        self.scale = self.breite / self.linelength[0]
        self.opticalSize()        
        self.new_page()
        pagebreak = True

        
        x=0
        y=0
        linebreak = 0
        
        for i,gn in enumerate(my_list):
                        
            if gn == r"\n":
                linebreak += 1
                self.scale = self.breite / self.linelength[linebreak]
                self.opticalSize() 
                yadv = self.upm * self.scale + self.y_pad
                y += yadv
                translate(-x, -yadv * self.linespace)
                x = 0 #+ xadv
            elif not gn in self.font:
                print "Missing glyph:", gn
            else:
                glyph = self.font[gn]
                if i < len(my_list)-1:
                    xadv = (glyph.width + self.kerning.getKernValue(gn,my_list[i+1])) * self.scale
                    
                    #print Kerning pairs
                    #if not self.kerning.getKernValue(gn,my_list[i+1]) == 0:
                    #    print "Kerned:", gn, my_list[i+1], self.kerning.getKernValue(gn,my_list[i+1])
                    
                else:
                    xadv = glyph.width * self.scale
               
                if (x + xadv) > self.width - self.margins["left"] - 0.9*self.margins["right"]:
                    yadv = self.upm * self.scale + self.y_pad
                    y += yadv
                    translate(-x, -yadv)
                    self._drawGlyph(glyph) 
                    x = 0 + xadv
                
                else:
                    self._drawGlyph(glyph)
                    x += xadv
                translate(xadv, 0)
        if self.send_to_plotter:
            saveImage(expanduser("~/Documents/Penplotter_Cards/Postcard_%s_%d.pdf") % (Line_1, now()))
            print "PDF saved to /Documents/Penplotter_Cards/Postcard_%s_%d.pdf" % (Line_1, now())
            print "Plotting..."
            plot("~/Desktop/temp.hpgl")
            
                    
    def opticalSize(self):
        fontsize_list = {
        0 :Font(expanduser("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_Centerline.ufo")),
        4: Font (expanduser("~//Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_fourlines_01.ufo")),
        2: Font (expanduser("~//Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_oneline_01.ufo")),
        1: Font (expanduser("~//Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_Outline_01.ufo")),
        3: Font (expanduser("~//Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_twoline_01.ufo")),
        #5: Font (expanduser("~//Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/petrosian_04.ufo"),
        }
        
        if self.font_index == 2: 
            self.font = fontsize_list[ min( 4, int(self.scale/0.069) ) ] 
                     
                
if __name__ == '__main__':
    v = Variable([
        dict(name="Line_1", ui="EditText",
            args=dict({"continuous":False},text="Postcard-Setter"),
        ),
        dict(name="Line_2", ui="EditText",
            args=dict({"continuous":False},text="------------------"),
        ),
        dict(name="Line_3", ui="EditText",
            args=dict({"continuous":False},text="Each line of text is"),
        ),
        dict(name="Line_4", ui="EditText",
            args=dict({"continuous":False},text="transformed"),
        ),
        dict(name="Line_5", ui="EditText",
            args=dict({"continuous":False},text="to the same width."),
        ),
        
        
        dict(name="Fonts", ui="RadioGroup",
            args=dict( 
                #posSize=(10, 10, -10, 40),
                titles=["FF Mark", "FF Hertz Mono", "Bronco", "Broadnib"],
                isVertical=True,
            )
        ),
         dict(name="All_Caps", ui="CheckBox",
             args=dict(value=False)
         ),
        dict(name="Leading", ui="Slider",
            args=dict( 
                {"continuous":False},
                value=0.7, 
                minValue=0.1, 
                maxValue=1.1
            )
        ),
        dict(name="Move_vertical", ui="Slider",
            args=dict( 
                {"continuous":False},
                value=20, 
                minValue=-80, 
                maxValue=240
            )
        ),
        dict(name="Scale", ui="Slider",
            args=dict( 
                {"continuous":False},
                value=240, 
                minValue=0, 
                maxValue=240
            )
        ),
        dict(name="SimulateNib", ui="CheckBox",
            args=dict(value=False)
        ),
        dict(name="ParallelPen", ui="RadioGroup",
            args=dict( 
                titles=["5.0", "3.8", "2.4", "1.5"],
                isVertical=False,
            )
        ),
        dict(name="NibAngle", ui="Slider",
            args=dict( 
                value=30, 
                minValue=-90, 
                maxValue=90,
            )
        ),
        dict(name="ColorNib", ui="CheckBox",
            args=dict(value=False)
        ),
        dict(name="SendToPlotter", ui="CheckBox",
            args=dict(value=False)
        ),
        
        
    ], globals())
            
    
    print "FONTS\n-----\n", "1: FF Mark\n", "2: FF Hertz Mono\n", "3: Bronco\n", "4: Broadnib\n"
    
    fp = FontProofer(
        font_index=Fonts,
        linespace=Leading,
        marginsupdown=Move_vertical,
        marginsside=(260 - Scale),
        nib_simulate=SimulateNib,
        nib_width_index=ParallelPen,
        nib_angle=NibAngle,
        Color_Nib=ColorNib,
        send_to_plotter=SendToPlotter,
        )
        
    lines = [Line_1,Line_2,Line_3,Line_4, Line_5]
    final_text = "\n".join( [l for l in lines if l] )
      
    if All_Caps or Fonts == 2:
        if not Fonts == 3:
            final_text = final_text.upper()
            print "CAPS LOCK AND ROLL"
        else:
            print "No caps lock adviced for this typeface"
    
    fp.setText(final_text) 
    fp.getPickedFont
    
