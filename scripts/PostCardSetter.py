from __future__ import absolute_import
from fontTools.agl import UV2AGL
import sys
sys.path.append("/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7")
import chiplotle
from defcon import Font
from compositor import Font as FeatureFont
from drawBot.drawBotDrawingTools import _drawBotDrawingTool
from fontTools.pens.cocoaPen import CocoaPen
import subprocess
from os.path import expanduser
import os
from time import mktime, gmtime
from vanilla import *
from drawbotPlotter.HPGLContext import addHPGLContext
from drawbotPlotter.HPGLDraw import HPGLDraw
from drawBot.context import allContexts

addHPGLContext()

# Set min/max curve splitting values in HPGL context
hc = allContexts[-1]
hc.min_segment_units = 20
hc.max_curve_steps = 50


DEBUG = True


def now(): 
   return mktime(gmtime()) 



class SimpleGlyphRecord(object):
    def __init__(self, glyphName, xPlacement=0, yPlacement=0, xAdvance=0, yAdvance=0):
        self.glyphName = glyphName
        self.xPlacement = xPlacement
        self.yPlacement = yPlacement
        self.xAdvance = xAdvance
        self.yAdvance = yAdvance



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
    0:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Mark_CenterLine_03.ufo",
            None,
        ),
    1:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/HertzTypewriterLine-Light.ufo",
            None,
        ),
    2:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_outline_01.ufo",
            None,
        ),
    3:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/manVSmachine7.ufo",
            None,
        ),
    4:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/LiebeLotte-Centerline.ufo",
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/LiebeLotte-Centerline.otf",
        ),
    5:  (
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/ComicJens-Hairline.ufo",
            "~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/ComicJens-Hairline.otf",
        ),
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
    
    def __init__(self, font=None, format_index=0, font_index=0, caps_lock=False, linespace=0.7, marginsupdown = 20, marginsside = 20, nib_simulate=False, nib_width_index=0, nib_angle=30, Color_Nib=False, send_to_plotter=False):       
        
        self.linespace = linespace
        self.format_index = format_index
        self.font_index = font_index
        self.set_font(font)    
        
        self.mark_fill = False
        self.mark_composites = False
        
        # A6 Format
        hpglscale = 1.3752
        self.width = 842/2 *hpglscale
        self.height = 595/2 *hpglscale
        if format_index == 1:
            self.width = 595/2 *hpglscale
            self.height = 842/2 *hpglscale
        
        
        self.margins = {
            "top": marginsupdown,
            "bottom": marginsupdown,
            "left": marginsside,
            "right": marginsside,
        
        }
        self.breite = self.width - marginsside * 1.5*hpglscale
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
        
        # open UFO with defcon
        if font is not None:
            font_path = expanduser(font[0])
            self.font = Font(font_path)
        
            # open OTF with compositor
            if font[1] is None:
                shaping_font_path = None
                self.shaping_font = None
            else:
                shaping_font_path = expanduser(font[1])
                self.shaping_font = FeatureFont(shaping_font_path)
        else:
            self.font = None
            self.shaping_font = None
        
        if self.font is not None:
            self.upm = self.font.info.unitsPerEm
            self.desc = self.font.info.descender
            self.x_height = self.font.info.xHeight
            self.cap_height = self.font.info.capHeight
            self.asc = self.font.info.ascender
            self.angle = self.font.info.italicAngle
        
        else:
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
        #scale(self.scale)
        
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
    
    def setText(self, my_text):
        my_list = getGlyphNamesFromString(my_text+"\n")
        
        if self.font is None:
            print "Pick a font"
            return None
        
        if self.shaping_font is None:
            glyphRecords = [SimpleGlyphRecord(n) for n in my_list]
        else:
            for tag, state in [
                ("calt", True),
                ("liga", True),
                ("kern", True),
            ]:
                self.shaping_font.gpos.setFeatureState(tag, state)
            for tag, state in [
                ("calt", True),
                ("liga", True),
            ]:
                self.shaping_font.gsub.setFeatureState(tag, state)
            glyphRecords = self.shaping_font.process(
                my_list,
                script="DFLT",
                langSys="DEU",
                rightToLeft=False,
                case="unchanged",
            )
        
        # Measure lines, draw line when a \n character occurs.
        
        line_width = 0
        line_width_prev = 0
        lineGlyphRecords = []
        first_line = True
        
        for gr in glyphRecords:
            if gr.glyphName != r"\n":
                glyphname = gr.glyphName
                try:
                    glyph = self.font[glyphname]
                except KeyError:
                    print "Ignored missing glyph:", glyphname
                    glyph = None
                if glyph is not None:
                    line_width += glyph.width + gr.xAdvance
                    lineGlyphRecords.append(gr)
            else:
                #print [gr.glyphName for gr in lineGlyphRecords]
                #print "Line width:", line_width
                self.scale = self.breite / line_width
                #print "Scale:", self.scale
                if first_line:
                    self.new_page()
                    first_line = False
                else:
                    #print "Translate"
                    translate(0, -self.upm * self.scale * self.linespace)
                    #rect(0, 0, 10, 10)
                self.opticalSize()
                save()
                scale(self.scale)
                #fill(None)
                #stroke(1,0,0)
                #rect(0, 10, line_width, self.asc-10)
                #rect(0, self.desc, line_width, -self.desc-10)
                for gr in lineGlyphRecords:
                    glyphname = gr.glyphName
                    glyph = self.font[glyphname]
                    save()
                    translate(gr.xPlacement, gr.yPlacement)
                    self._drawGlyph(glyph)
                    restore()
                    translate(glyph.width + gr.xAdvance, gr.yAdvance)
                line_width = 0
                lineGlyphRecords = []
                restore()
                
        if self.send_to_plotter:
            saveImage(expanduser("~/Documents/Penplotter_Cards/Postcard_%s_%d.pdf") % (Line_1, now()))
            print "PDF saved to /Documents/Penplotter_Cards/Postcard_%s_%d.pdf" % (Line_1, now())
            print "Plotting..."
            plot("~/Desktop/temp.hpgl")
    
                    
    def opticalSize(self):
        fontsize_list = {
        0: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_Centerline.ufo", None),
        4: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_fourlines_01.ufo", None),
        2: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_oneline_01.ufo", None),
        1: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_Outline_01.ufo", None),
        3: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/Bronco_twoline_01.ufo", None),
        #5: ("~/Documents/Schriften/_MeineSchriften/PenPlotterFaces/DrawbotSketches/fonts/petrosian_04.ufo", None),
        }
        
        if self.font_index == 2: 
            self.set_font(fontsize_list[ min( 4, int(self.scale/0.069) ) ] )
                     
                
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
        
        dict(name="Format", ui="RadioGroup",
            args=dict( 
                titles=["Landscape", "Portrait"],
                isVertical=True,
            )
        ),
        
        dict(name="Fonts", ui="RadioGroup",
            args=dict( 
                titles=["FF Mark", "FF Hertz Mono", "Bronco", "Broadnib", "LiebeLotte", "Comic Jens"],
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
        format_index=Format,
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
    
