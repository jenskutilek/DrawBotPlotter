from drawbotPlotter.HPGLContext import addHPGLContext
from drawbotPlotter.HPGLDraw import HPGLDraw
from drawBot.context import allContexts

addHPGLContext()

hc = allContexts[-1]
hc.min_segment_units = 20
hc.max_curve_steps = 50

#size("A3Landscape") # 1190 * 842
size(1145, 782)
fill(None)
strokeWidth(1)
stroke(1, 0, 0)
rect(0, 0, 72, 72)
stroke(0, 0, 0)
rect(width()-72, height()-72, 72, 72)
save()
translate(width()/2, height()/2)
stroke(0, 0, 1)
strokeWidth(2)
if False:
    w = 2
    for i in range(10):
        rect(-36, -36, 72, 72)
        #fill(1, 1, 1, .6)
        rect(180, 0, 72, 72)
        rotate(10)
        scale(1.2)
        w /= 1.2
        strokeWidth(w)
restore()
stroke(0, 0, 1)
oval(537, 355, 72, 72)
d = 300
translate((width()-d)/2, (height()-d)/2)
translate(-d, 0)
stroke(0, 1, 0)
oval(0, 0, d, d)
    
if False:
    save()
    d = 300
    translate((width()-d)/2, (height()-d)/2)
    translate(-d, 0)
    oval(0, 0, d, d)
    translate(d, 0)
    save()
    scale(0.5)
    oval(0, 0, d*2, d*2)
    restore()
    translate(d, 0)
    scale(2)
    oval(0, 0, d/2, d/2)
    restore()
translate(72, 72)
if False:
    path = BezierPath()
    path.moveTo((0, 0))
    path.curveTo((55, 0), (100, 45), (100, 100))
    path.endPath()
    drawPath(path)

#translate(200, 200)
#rect(-100, -100, 72, 72)

saveImage("~/Desktop/HPGLContext.hpgl")
#saveImage("~/Desktop/HPGLContext.pdf")

# To test the result, draw the HPGL file in DrawBot

HPGLDraw("~/Desktop/HPGLContext.hpgl", 1145, 782)