# For the GMLs without the environment tag.
# Screen x and y should manually set here
DEFAULT_SCREEN_X = 480
DEFAULT_SCREEN_Y = 320

#############################
## CLASS DEFINITIONS START ##
#############################
class Tag:
    def __init__(self):
        self.header = Header()
        self.environment = Environment()
        self.drawing = Drawing()

class Header:
    def __init__(self):
        self.client = Client()

class Client:
    def __init__(self):
        self.name = ""
        self.version = ""
        self.username = ""
        self.keywords = ""
        self.uniqueKey = ""

class Drawing:
    def __init__(self):
        self.strokes = []


class Stroke:
    def __init__(self):
        self.brush = Brush()
        self.points = []

class Brush:
    def __init__(self):
        self.color = [0,0,0]
        self.layerRelative = 0;

class Point:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.t = 0

class ScreenBounds:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

class Environment:
    def __init__(self):
        self.screenbounds = ScreenBounds()
        self.up = [0,0,0]

###########################
## CLASS DEFINITIONS END ##
###########################

#-------------------------#

######################
## GML PARSER START ##
######################
import xml.dom.minidom
from xml.dom.minidom import parse, parseString


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        return ''.join(rc)

# getText() wrappers to handle missing nodes
def getTextFromNode(name, node, default=''):
    try:
        return getText(node.getElementsByTagName(name)[0].childNodes)
    except:
        return default

def getNumberFromNode(name, node, default='0'):
    return getTextFromNode(name, node, default)


class GMLParser:
    def __init__(self, gmlData):
        self.gmlData = gmlData
        self.dom = None
        self.tag = Tag()

        self.header = Header()
        self.client = Client()
        self.header.client = self.client
        self.environment = Environment()
        self.screenbounds = ScreenBounds()
        self.drawing = Drawing()
#        self.strokes = Stroke()

    def gmlParser(self, gmlData):
        self.dom = parseString(gmlData);


    def handleTag(self, tag):
        self.tag.header = self.header
        self.tag.environment = self.environment
        self.tag.drawing = self.drawing

        if tag.getElementsByTagName("header"):
            self.handleHeader(tag.getElementsByTagName("header")[0])

        if tag.getElementsByTagName("environment"):
            self.handleEnvironment(tag.getElementsByTagName("environment")[0])
        else:
            self.environment.up = [1.0, 0.0, 0.0]
            screenbounds = ScreenBounds()
            screenbounds.x = DEFAULT_SCREEN_X
            screenbounds.y = DEFAULT_SCREEN_Y
            screenbounds.z = 0
            self.environment.screenbounds = screenbounds

        self.handleDrawing(tag.getElementsByTagName("drawing")[0])

    def handleHeader(self, header):
        self.client.name = getTextFromNode("name", header)
        self.client.version = getTextFromNode("version", header)
        self.client.username = getTextFromNode("username", header)
        self.client.keywords = getTextFromNode("keywords", header)
        self.client.uniqueKey = getTextFromNode("uniqueKey", header)
        self.header.client = self.client

    def handleEnvironment(self, environment):
        up_vec = [0,0,0]
        tag = environment.getElementsByTagName("up")
        if tag:
            up = tag[0]
            up_vec[0] = float(getText(up.getElementsByTagName("x")[0].childNodes))
            up_vec[1] = float(getText(up.getElementsByTagName("y")[0].childNodes))
            up_vec[2] = float(getText(up.getElementsByTagName("z")[0].childNodes))
        else:
            up_vec = [0.0, 0.0, 0.0]

        self.environment.up = up_vec

        tag = environment.getElementsByTagName("screenBounds")
        # Defaults set elsewhere...
        if tag:
            screenbounds = tag[0]
            self.screenbounds.x = float(getText(screenbounds.getElementsByTagName("x")[0].childNodes))
            self.screenbounds.y = float(getText(screenbounds.getElementsByTagName("y")[0].childNodes))
            self.screenbounds.z = float(getText(screenbounds.getElementsByTagName("z")[0].childNodes))
            self.environment.screenbounds = self.screenbounds
        else:
            screenbounds = ScreenBounds()
            screenbounds.x = DEFAULT_SCREEN_X
            screenbounds.y = DEFAULT_SCREEN_Y
            screenbounds.z = 0
            self.environment.screenbounds = screenbounds            


    def handleDrawing(self, drawing):
        for stroke in drawing.getElementsByTagName("stroke"):
            sobject = self.handleStroke(stroke)
            self.drawing.strokes.append(sobject)


    def handleStroke(self, stroke):
        s = Stroke();
        s.brush = None
        s.points = []

        for point in stroke.getElementsByTagName("pt"):
            p = Point()
            # Manual 90-degree-rotated iPhone transformation: (x,y) => (y,1-x)
            if self.environment.up == [1.0,0.0,0.0]:
              p.x = float(getText(point.getElementsByTagName("y")[0].childNodes))
              p.y = 1.0 - float(getText(point.getElementsByTagName("x")[0].childNodes))
            else:
              p.x = float(getText(point.getElementsByTagName("x")[0].childNodes))
              p.y = float(getText(point.getElementsByTagName("y")[0].childNodes))

            p.z = float(getNumberFromNode('z', point))
            p.t = float(getNumberFromNode('time', point))
            s.points.append(p)

        return s

    def handleGML(self):
        self.gmlParser(self.gmlData)
        self.handleTag(self.dom.getElementsByTagName("tag")[0])
        return self.tag

####################
## GML PARSER END ##
####################

#-------------------------#

############################
## GMLIMAGERENDERER START ##
############################
import Image, ImageDraw, sys
import ImageFilter

import math

class GMLImageRenderer:
    def __init__(self, tag):
        self.tag = tag

    def render(self, filename):

        sx = self.tag.environment.screenbounds.x
        sy = self.tag.environment.screenbounds.y

        im = Image.new("RGB", [int(sx), int(sy)])
        draw = ImageDraw.Draw(im)



        for stroke in self.tag.drawing.strokes:
            # temp variables
            pi = 0
            pj = 0

            for point in stroke.points:
                # scale the points according to screenbounds
                x = point.x*sx
                y = point.y*sy
                # for the first point
                pi = x if (pi==0) else pi
                pj = y if (pj==0) else pj
                # start drawing
                draw.line((x,y)+(pi,pj), fill=(20,20,20), width=8)
                draw.line((x,y)+(pi,pj), fill=(255,255,255), width=5)
                # end drawing
                pi = x
                pj = y

        del draw

        im = im.filter(ImageFilter.SMOOTH)
#        im = im.filter(ImageFilter.SMOOTH_MORE)
#        im = im.filter(ImageFilter.CONTOUR)
#        im = im.filter(ImageFilter.DETAIL)

        im.save(filename, "PNG")

##########################
## GMLIMAGERENDERER END ##
##########################

#-------------------------#

######################
## GMLFETCHER START ##
######################
import urllib2
DATA_URL = "http://000000book.com/data/"

class GMLFetcher:
    def __init__(self,id):
        response = urllib2.urlopen('%s%s.gml'%(DATA_URL,str(id)))
        contents = response.read()

        gmlParser = GMLParser(contents)
        self.tag = gmlParser.handleGML()
####################
## GMLFETCHER END ##
####################

#-------------------------#

def readfile(filename):
    contents = ""
    f = open(filename,'r')
    for line in f.readlines():
        contents = contents + line
    f.close()

    return contents


######### RUN ############
if(len(sys.argv) > 3 and sys.argv[1] == "-file"):
    contents = readfile(sys.argv[2])
    gmlParser = GMLParser(contents)
    gmlRenderer = GMLImageRenderer(gmlParser.handleGML())
    gmlRenderer.render(sys.argv[3])

elif(len(sys.argv) > 3 and sys.argv[1] == "-id"):
    fetchedGML = GMLFetcher(sys.argv[2])
    gmlRenderer = GMLImageRenderer(fetchedGML.tag)
    gmlRenderer.render(sys.argv[3])

else:
    print "Usage: python GMLImageRenderer.py -file file.gml output.png (will load local file)"
    print "or"
    print "Usage: python GMLImageRenderer.py -id gml_id output.png (will fetch from "+DATA_URL+")"


