from __future__ import division

from matplotlib import rcParams
from numerix import array, arange, sin, cos, pi, Float
from artist import Artist
from cbook import True, False, enumerate, popd
from colors import colorConverter
from transforms import bound_vertices

class Patch(Artist):
    """
    A patch is a 2D thingy with a face color and an edge color

    If any of edgecolor, facecolor, linewidth, or antialiased are
    None, they default to their rc params setting

    """
    zlevel = 1
    def __init__(self,
                 edgecolor=None,   
                 facecolor=None,
                 linewidth=None,
                 antialiased = None,
                 fill=1,
                 **kwargs
                 ):
        Artist.__init__(self)

        if edgecolor is None: edgecolor = rcParams['patch.edgecolor']
        if facecolor is None: facecolor = rcParams['patch.facecolor']
        if linewidth is None: linewidth = rcParams['patch.linewidth']
        if antialiased is None: antialiased = rcParams['patch.antialiased']

        self._edgecolor = edgecolor
        self._facecolor = facecolor
        self._linewidth = linewidth
        self._antialiased = antialiased        
        self.fill = fill


        for k,v in kwargs.items():
            func = 'set_' + k            
            if hasattr(self, func):
                func = getattr(self, func)
                func(v)
        
    def copy_properties(self, other):
        self._edgecolor = other._edgecolor
        self._facecolor = other._facecolor
        self.fill = other.fill
        self._linewidth= other._linewidth

    def get_antialiased(self):
        return self._antialiased

    def get_edgecolor(self):
        return self._edgecolor

    def get_facecolor(self):
        return self._facecolor
        
    def get_linewidth(self):
        return self._linewidth

    def set_antialiased(self, aa):
        """
Set whether to use antialiased rendering

ACCEPTS: [True | False]
"""
        self._antialiased = aa

    def set_edgecolor(self, color):
        """
Set the patch edge color

ACCEPTS: any matplotlib color - see help(colors)
"""
        self._edgecolor = color

    def set_facecolor(self, color):
        """
Set the patch face color

ACCEPTS: any matplotlib color - see help(colors)
"""
        self._facecolor = color

    def set_linewidth(self, w):
        """
Set the patch linewidth in points

ACCEPTS: float
"""
        self._linewidth = w

    def set_fill(self, b):
        """
Set whether to fill the patch

ACCEPTS: [True | False]
"""
        self.fill = b

    
    def draw(self, renderer):

        #renderer.open_group('patch')
        gc = renderer.new_gc()
        gc.set_foreground(self._edgecolor)
        gc.set_linewidth(self._linewidth)
        gc.set_alpha(self._alpha)
        gc.set_antialiased(self._antialiased)
        if self.get_clip_on(): gc.set_clip_rectangle(
            self.clipbox.get_bounds())
        gc.set_capstyle('projecting')

        if not self.fill or self._facecolor is None: rgbFace = None
        else: rgbFace = colorConverter.to_rgb(self._facecolor)

        verts = self.get_verts()        
        tverts = self._transform.seq_xy_tups(verts)

        renderer.draw_polygon(gc, rgbFace, tverts)

        #renderer.close_group('patch')
        
    def get_verts(self):
        """
        Return the vertices of the patch
        """
        raise NotImplementedError('Derived must override')

    def get_window_extent(self, renderer=None):
        verts = self.get_verts()
        tverts = self._transform.seq_xy_tups(verts)
        return bound_vertices(tverts)



    def set_lw(self, val):
        'alias for set_linewidth'
        self.set_linewidth(val)
    

    def set_ec(self, val):
        'alias for set_edgecolor'
        self.set_edgecolor(val)
    

    def set_fc(self, val):
        'alias for set_facecolor'
        self.set_facecolor(val)


    def get_aa(self):
        'alias for get_antialiased'
        return self.get_antialiased()
    

    def get_lw(self):
        'alias for get_linewidth'
        return self.get_linewidth()
    

    def get_ec(self):
        'alias for get_edgecolor'
        return self.get_edgecolor()
    

    def get_fc(self):
        'alias for get_facecolor'
        return self.get_facecolor()
        
class Rectangle(Patch):
    """
    Draw a rectangle with lower left at xy=(x,y) with specified
    width and height

    """

    def __init__(self, xy, width, height,
                 **kwargs):
        """
        xy is an x,y tuple lower, left

        width and height are width and height of rectangle

        fill is a boolean indicating whether to fill the rectangle

        """
                     
        Patch.__init__(self, **kwargs)

        self.xy  = array(xy, Float)
        self.width, self.height = width, height

    def get_verts(self):
        """
        Return the vertices of the rectangle
        """
        x, y = self.xy
        return ( (x, y), (x, y+self.height),
                 (x+self.width, y+self.height), (x+self.width, y),
                 )
        
    def get_x(self):
        "Return the left coord of the rectangle"
        return self.xy[0]

    def get_y(self):
        "Return the bottom coord of the rectangle"
        return self.xy[1]

    def get_width(self):
        "Return the width of the  rectangle"
        return self.width

    def get_height(self):
        "Return the height of the rectangle"
        return self.height

    def set_x(self, x):
        """
Set the left coord of the rectangle

ACCEPTS: float
"""     
        self.xy[0] = x

    def set_y(self, y):
        """
Set the bottom coord of the rectangle

ACCEPTS: float
"""
        self.xy[1] = y

    def set_width(self, w):
        """
Set the width rectangle

ACCEPTS: float
"""
        self.width = w

    def set_height(self, h):
        """
Set the width rectangle

ACCEPTS: float
"""
        self.height = h

    def set_bounds(self, *args):
        """
Set the bounds of the rectangle: l,b,w,h

ACCEPTS: (left, bottom, width, height)
"""
        if len(args)==0:
            l,b,w,h = args[0]
        else:
            l,b,w,h = args
        self.xy = array([float(l),float(b)])
        self.width = w
        self.height = h

    
class RegularPolygon(Patch):
    """
    A regular polygon patch.  xy is a length 2 tuple (the center)
    numVertices is the number of vertices.  Radius is the distance
    from the center to each of the vertices.  Orientation is in
    radians and rotates the polygon.


    """
    def __init__(self, xy, numVertices, radius=5, orientation=0,
                 **kwargs):

        Patch.__init__(self, **kwargs)

        self.xy = xy
        self.numVertices = numVertices
        self.radius = radius
        self.orientation = orientation

        theta = 2*pi/self.numVertices*arange(self.numVertices) + \
                self.orientation
        r = self.radius
        xs = self.xy[0] + r*cos(theta)
        ys = self.xy[1] + r*sin(theta)
        
        self.verts = zip(xs, ys)

    def get_verts(self):
        return self.verts

class Polygon(Patch):
    """
    A general polygon patch.  xy is a sequence of x,y 2 tuples tuples
    """
    def __init__(self, xy, **kwargs):
        Patch.__init__(self, **kwargs)
        self.xy = xy

    def get_verts(self):
        return self.xy
    
    
class Circle(RegularPolygon):
    """
    A circle patch
    """
    def __init__(self, xy, radius=5,
                 resolution=20,  # the number of vertices
                 **kwargs
                 ):
        RegularPolygon.__init__(self, xy,
                                resolution,
                                radius,
                                orientation=0,
                                **kwargs)
        
def bbox_artist(artist, renderer, props=None):
    """
    This is a debug function to draw a rectangle around the bounding
    box returned by get_window_extent of an artist, to test whether
    the artist is returning the correct bbox

    props is a dict of rectangle props with the additional property
    'pad' that sets the padding around the bbox in points
    """
    if props is None: props = {}
    pad = popd(props, 'pad', 4)
    pad = renderer.points_to_pixels(pad)
    bbox = artist.get_window_extent(renderer)
    l,b,w,h = bbox.get_bounds()
    l-=pad/2.
    b-=pad/2.
    w+=pad
    h+=pad
    r = Rectangle(xy=(l,b), 
                  width=w, 
                  height=h, 
                  )
    r.set_clip_on( False )
    r.update(props)
    r.draw(renderer)
    

def draw_bbox(bbox, renderer, color='k', trans=None):
    """
    This is a debug function to draw a rectangle around the bounding
    box returned by get_window_extent of an artist, to test whether
    the artist is returning the correct bbox
    """

    l,b,w,h = bbox.get_bounds()
    r = Rectangle(xy=(l,b), 
                  width=w, 
                  height=h,
                  edgecolor=color,
                  fill=False,
                  )
    if trans is not None: r.set_transform(trans)
    r.set_clip_on( False )
    r.draw(renderer)

