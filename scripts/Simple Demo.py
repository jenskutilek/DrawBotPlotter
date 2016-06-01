from drawbotPlotter.HPGLContext import addHPGLContext
from drawbotPlotter.HPGLDraw import HPGLDraw

addHPGLContext()

#size("A3Landscape") # 1190 * 842
size(1145, 782)
fill(None)
strokeWidth(1)
stroke(0)
stroke(1, 0, 0)
rect(0, 0, 72, 72)
stroke(0, 0, 0)
rect(width()-72, height()-72, 72, 72)
save()
translate(width()/2, height()/2)
stroke(0, 0, 1)
strokeWidth(2)
rect(-36, -36, 72, 72)
restore()
oval(537, 355, 72, 72)
d = 300
#oval((width()-d)/2, (height()-d)/2, d, d)
path = BezierPath()
path.moveTo((0, 0))
path.curveTo((55, 0), (100, 45), (100, 100))
path.endPath()
drawPath(path)
saveImage("~/Desktop/HPGLContext.hpgl")

# To test the result, draw the HPGL file in DrawBot

HPGLDraw("~/Desktop/HPGLContext.hpgl", 1145, 782)