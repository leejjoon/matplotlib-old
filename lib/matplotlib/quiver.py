'''
Support for plotting fields of arrows.

Presently this contains a single class, Quiver, but it
might make sense to consolidate other arrow plotting here.

This will also become a home for things such as standard
deviation ellipses, which can and will be derived very easily from
the Quiver code.
'''


_quiver_doc = '''
Plot a 2-D field of arrows.

Function signatures:

    quiver(U, V, **kw)
    quiver(U, V, C, **kw)
    quiver(X, Y, U, V, **kw)
    quiver(X, Y, U, V, C, **kw)

Arguments:

    X, Y give the x and y coordinates of the arrow locations
        (default is tail of arrow; see 'pivot' kwarg)
    U, V give the x and y components of the arrow vectors
    C is an optional array used to map colors to the arrows

    All arguments may be 1-D or 2-D arrays or sequences.
    If X and Y are absent, they will be generated as a uniform grid.
    If U and V are 2-D arrays but X and Y are 1-D, and if
        len(X) and len(Y) match the column and row dimensions
        of U, then X and Y will be expanded with meshgrid.

Keyword arguments (default given first):

  * units = 'width' | 'height' | 'dots' | 'inches' | 'x' | 'y'
            arrow units; the arrow dimensions *except for length*
            are in multiples of this unit.
  * scale = None | float
            data units per arrow unit, e.g. m/s per plot width;
            a smaller scale parameter makes the arrow longer.
            If None, a simple autoscaling algorithm is used, based
            on the average vector length and the number of vectors.

    Arrow dimensions and scales can be in any of several units:

    'width' or 'height': the width or height of the axes
    'dots' or 'inches':  pixels or inches, based on the figure dpi
    'x' or 'y': X or Y data units

    In all cases the arrow aspect ratio is 1, so that if U==V the angle
    of the arrow on the plot is 45 degrees CCW from the X-axis.

    The arrows scale differently depending on the units, however.
    For 'x' or 'y', the arrows get larger as one zooms in; for other
    units, the arrow size is independent of the zoom state.  For
    'width or 'height', the arrow size increases with the width and
    height of the axes, respectively, when the the window is resized;
    for 'dots' or 'inches', resizing does not change the arrows.


  * width = ?       shaft width in arrow units; default depends on
                        choice of units, above, and number of vectors;
                        a typical starting value is about
                        0.005 times the width of the plot.
  * headwidth = 3    head width as multiple of shaft width
  * headlength = 5   head length as multiple of shaft width
  * headaxislength = 4.5  head length at shaft intersection
  * minshaft = 1     length below which arrow scales, in units
                        of head length. Do not set this to less
                        than 1, or small arrows will look terrible!
  * minlength = 1    minimum length as a multiple of shaft width;
                     if an arrow length is less than this, plot a
                     dot (hexagon) of this diameter instead.

    The defaults give a slightly swept-back arrow; to make the
    head a triangle, make headaxislength the same as headlength.
    To make the arrow more pointed, reduce headwidth or increase
    headlength and headaxislength.
    To make the head smaller relative to the shaft, scale down
    all the head* parameters.
    You will probably do best to leave minshaft alone.

  * pivot = 'tail' | 'middle' | 'tip'
        The part of the arrow that is at the grid point; the arrow
        rotates about this point, hence the name 'pivot'.

  * color = 'k' | any matplotlib color spec or sequence of color specs.
        This is a synonym for the PolyCollection facecolor kwarg.
        If C has been set, 'color' has no effect.

   * All PolyCollection kwargs are valid, in the sense that they
        will be passed on to the PolyCollection constructor.
        In particular, one might want to use, for example:
            linewidths = (1,), edgecolors = ('g',)
        to make the arrows have green outlines of unit width.

'''

_quiverkey_doc = '''
Add a key to a quiver plot.

Function signature:
    quiverkey(Q, X, Y, U, label, **kw)

Arguments:
    Q is the Quiver instance returned by a call to quiver.
    X, Y give the location of the key; additional explanation follows.
    U is the length of the key
    label is a string with the length and units of the key

Keyword arguments (default given first):
  * coordinates = 'axes' | 'figure' | 'data' | 'inches'
        Coordinate system and units for X, Y: 'axes' and 'figure'
        are normalized coordinate systems with 0,0 in the lower
        left and 1,1 in the upper right; 'data' are the axes
        data coordinates (used for the locations of the vectors
        in the quiver plot itself); 'inches' is position in the
        figure in inches, with 0,0 at the lower left corner.
  * color overrides face and edge colors from Q.
  * labelpos = 'N' | 'S' | 'E' | 'W'
        Position the label above, below, to the right, to the left
        of the arrow, respectively.
  * labelsep = 0.1 inches distance between the arrow and the label
  * labelcolor (defaults to default Text color)
  * fontproperties is a dictionary with keyword arguments accepted
        by the FontProperties initializer: family, style, variant,
        size, weight

    Any additional keyword arguments are used to override vector
    properties taken from Q.

    The positioning of the key depends on X, Y, coordinates, and
    labelpos.  If labelpos is 'N' or 'S', X,Y give the position
    of the middle of the key arrow.  If labelpos is 'E', X,Y
    positions the head, and if labelpos is 'W', X,Y positions the
    tail; in either of these two cases, X,Y is somewhere in the middle
    of the arrow+label key object.
'''

from matplotlib.collections import PolyCollection
from matplotlib.mlab import meshgrid
from matplotlib import numerix as nx
from matplotlib import transforms as T
from matplotlib.text import Text
from matplotlib.artist import Artist
from matplotlib.font_manager import FontProperties
import math


class QuiverKey(Artist):
    ''' Labelled arrow for use as a quiver plot scale key.
    '''
    halign = {'N': 'center', 'S': 'center', 'E': 'left',   'W': 'right'}
    valign = {'N': 'bottom', 'S': 'top',    'E': 'center', 'W': 'center'}
    pivot  = {'N': 'mid',    'S': 'mid',    'E': 'tip',    'W': 'tail'}

    def __init__(self, Q, X, Y, U, label, **kw):
        Artist.__init__(self)
        self.Q = Q
        self.X = X
        self.Y = Y
        self.U = U
        self.coord = kw.pop('coordinates', 'axes')
        self.color = kw.pop('color', None)
        self.label = label
        self.labelsep = T.Value(kw.pop('labelsep', 0.1)) * Q.ax.figure.dpi
        self.labelpos = kw.pop('labelpos', 'N')
        self.labelcolor = kw.pop('labelcolor', None)
        self.fontproperties = kw.pop('fontproperties', dict())
        self.kw = kw
        self.text = Text(text=label,
                         horizontalalignment=self.halign[self.labelpos],
                         verticalalignment=self.valign[self.labelpos],
                         fontproperties=FontProperties(**self.fontproperties))
        if self.labelcolor is not None:
            self.text.set_color(self.labelcolor)
        self._initialized = False
        self.zorder = Q.zorder + 0.1

    __init__.__doc__ = _quiverkey_doc

    def _init(self):
        if not self._initialized:
            self._set_transform()
            _pivot = self.Q.pivot
            self.Q.pivot = self.pivot[self.labelpos]
            self.verts = self.Q._make_verts(nx.array([self.U]), nx.zeros((1,)))
            self.Q.pivot = _pivot
            kw = self.Q.polykw
            kw.update(self.kw)
            self.vector = PolyCollection(self.verts,
                                         offsets=[(self.X,self.Y)],
                                         transOffset=self.get_transform(),
                                         **kw)
            if self.color is not None:
                self.vector.set_color(self.color)
            self.vector.set_transform(self.Q.get_transform())
            self._initialized = True

    def _text_x(self, x):
        if self.labelpos == 'E':
            return x + self.labelsep.get()
        elif self.labelpos == 'W':
            return x - self.labelsep.get()
        else:
            return x

    def _text_y(self, y):
        if self.labelpos == 'N':
            return y + self.labelsep.get()
        elif self.labelpos == 'S':
            return y - self.labelsep.get()
        else:
            return y

    def draw(self, renderer):
        self._init()
        self.vector.draw(renderer)
        x, y = self.get_transform().xy_tup((self.X, self.Y))
        self.text.set_x(self._text_x(x))
        self.text.set_y(self._text_y(y))
        self.text.draw(renderer)


    def _set_transform(self):
        if self.coord == 'data':
            self.set_transform(self.Q.ax.transData)
        elif self.coord == 'axes':
            self.set_transform(self.Q.ax.transAxes)
        elif self.coord == 'figure':
            self.set_transform(self.Q.ax.figure.transFigure)
        elif self.coord == 'inches':
            dx = ax.figure.dpi
            bb = T.Bbox(T.origin(), T.Point(dx, dx))
            trans = T.get_bbox_transform(T.unit_bbox(), bb)
            self.set_transform(trans)
        else:
            raise ValueError('unrecognized coordinates')
    quiverkey_doc = _quiverkey_doc

class Quiver(PolyCollection):
    '''
    Specialized PolyCollection for arrows.

    The only API method is set_UVC(), which can be used
    to change the size, orientation, and color of the
    arrows; their locations are fixed when the class is
    instantiated.  Possibly this method will be useful
    in animations.

    Much of the work in this class is done in the draw()
    method so that as much information as possible is available
    about the plot.  In subsequent draw() calls, recalculation
    is limited to things that might have changed, so there
    should be no performance penalty from putting the calculations
    in the draw() method.
    '''
    def __init__(self, ax, *args, **kw):
        self.ax = ax
        X, Y, U, V, C = self._parse_args(*args)
        self.X = X
        self.Y = Y
        self.N = len(X)
        self.scale = kw.pop('scale', None)
        self.headwidth = kw.pop('headwidth', 3)
        self.headlength = float(kw.pop('headlength', 5))
        self.headaxislength = kw.pop('headaxislength', 4.5)
        self.minshaft = kw.pop('minshaft', 1)
        self.minlength = kw.pop('minlength', 1)
        self.units = kw.pop('units', 'width')
        self.width = kw.pop('width', None)
        self.color = kw.pop('color', 'k')
        self.pivot = kw.pop('pivot', 'tail')
        kw.setdefault('facecolors', self.color)
        kw.setdefault('linewidths', (0,))
        PolyCollection.__init__(self, None, offsets=zip(X, Y),
                                       transOffset=ax.transData, **kw)
        self.polykw = kw
        self.set_UVC(U, V, C)
        self._initialized = False

        self.keyvec = None
        self.keytext = None

    __init__.__doc__ = '''
        The constructor takes one required argument, an Axes
        instance, followed by the args and kwargs described
        by the following pylab interface documentation:
        %s''' % _quiver_doc

    def _parse_args(self, *args):
        X, Y, U, V, C = [None]*5
        args = list(args)
        if len(args) == 3 or len(args) == 5:
            C = nx.ravel(args.pop(-1))
            #print 'in parse_args, C:', C
        V = nx.ma.asarray(args.pop(-1))
        U = nx.ma.asarray(args.pop(-1))
        nn = nx.shape(U)
        nc = nn[0]
        nr = 1
        if len(nn) > 1:
            nr = nn[1]
        if len(args) == 2:
            X, Y = [nx.ravel(a) for a in args]
            if len(X) == nc and len(Y) == nr:
                X, Y = [nx.ravel(a) for a in meshgrid(X, Y)]
        else:
            X, Y = [nx.ravel(a) for a in meshgrid(nx.arange(nc), nx.arange(nr))]
        return X, Y, U, V, C

    def _init(self):
        '''initialization delayed until first draw;
        allow time for axes setup.
        '''
        if not self._initialized:
            trans = self._set_transform()
            ax = self.ax
            sx, sy = trans.inverse_xy_tup((ax.bbox.width(), ax.bbox.height()))
            self.span = sx
            sn = max(8, min(25, math.sqrt(self.N)))
            if self.width is None:
                self.width = 0.06 * self.span / sn

    def draw(self, renderer):
        self._init()
        if self._new_UV:
            verts = self._make_verts(self.U, self.V)
            self.set_verts(verts)
            self._new_UV = False
        PolyCollection.draw(self, renderer)

    def set_UVC(self, U, V, C=None):
        self.U = nx.ma.ravel(U)
        self.V = nx.ma.ravel(V)
        if C is not None:
            self.set_array(nx.ravel(C))
        self._new_UV = True

    def _set_transform(self):
        ax = self.ax
        if self.units in ('x', 'y'):
            if self.units == 'x':
                dx0 = ax.viewLim.ur().x() - ax.viewLim.ll().x()
                dx1 = ax.bbox.ur().x() - ax.bbox.ll().x()
            else:
                dx0 = ax.viewLim.ur().y() - ax.viewLim.ll().y()
                dx1 = ax.bbox.ur().y() - ax.bbox.ll().y()
            dx = dx1/dx0
        else:
            if self.units == 'width':
                dx = ax.bbox.ur().x() - ax.bbox.ll().x()
            elif self.units == 'height':
                dx = ax.bbox.ur().y() - ax.bbox.ll().y()
            elif self.units == 'dots':
                dx = T.Value(1)
            elif self.units == 'inches':
                dx = ax.figure.dpi
            else:
                raise ValueError('unrecognized units')
        bb = T.Bbox(T.origin(), T.Point(dx, dx))
        trans = T.get_bbox_transform(T.unit_bbox(), bb)
        self.set_transform(trans)
        return trans

    def _make_verts(self, U, V):
        uv = U+V*1j
        uv = nx.ravel(nx.ma.filled(uv, nx.nan))
        a = nx.absolute(uv)
        if self.scale is None:
            sn = max(10, math.sqrt(self.N))
            scale = 1.8 * nx.average(a) * sn # crude auto-scaling
            scale = scale/self.span
            self.scale = scale
        length = a/(self.scale*self.width)
        X, Y = self._h_arrows(length)
        xy = (X+Y*1j) * nx.exp(1j*nx.angle(uv[...,nx.newaxis]))*self.width
        xy = xy[:,:,nx.newaxis]
        XY = nx.concatenate((xy.real, xy.imag), axis=2)
        return XY


    def _h_arrows(self, length):
        ''' length is in arrow width units '''
        minsh = self.minshaft * self.headlength
        N = len(length)
        length = nx.reshape(length, (N,1))
        x = nx.array([0, -self.headaxislength,
                        -self.headlength, 0], nx.Float64)
        x = x + nx.array([0,1,1,1]) * length
        y = 0.5 * nx.array([1, 1, self.headwidth, 0], nx.Float64)
        y = nx.repeat(y[nx.newaxis,:], N)
        x0 = nx.array([0, minsh-self.headaxislength,
                        minsh-self.headlength, minsh], nx.Float64)
        y0 = 0.5 * nx.array([1, 1, self.headwidth, 0], nx.Float64)
        ii = [0,1,2,3,2,1,0]
        X = nx.take(x, ii, 1)
        Y = nx.take(y, ii, 1)
        Y[:, 3:] *= -1
        X0 = nx.take(x0, ii)
        Y0 = nx.take(y0, ii)
        Y0[3:] *= -1
        shrink = length/minsh
        X0 = shrink * X0[nx.newaxis,:]
        Y0 = shrink * Y0[nx.newaxis,:]
        short = nx.repeat(length < minsh, 7, 1)
        #print 'short', length < minsh
        X = nx.where(short, X0, X)
        Y = nx.where(short, Y0, Y)
        if self.pivot[:3] == 'mid':
            X -= 0.5 * X[:,3, nx.newaxis]
        elif self.pivot[:3] == 'tip':
            X = X - X[:,3, nx.newaxis]   #numpy bug? using -= does not
                                         # work here unless we multiply
                                         # by a float first, as with 'mid'.
        tooshort = length < self.minlength
        if nx.any(tooshort):
            th = nx.arange(0,7,1, nx.Float64) * (nx.pi/3.0)
            x1 = nx.cos(th) * self.minlength * 0.5
            y1 = nx.sin(th) * self.minlength * 0.5
            X1 = nx.repeat(x1[nx.newaxis, :], N, 0)
            Y1 = nx.repeat(y1[nx.newaxis, :], N, 0)
            tooshort = nx.repeat(tooshort, 7, 1)
            X = nx.where(tooshort, X1, X)
            Y = nx.where(tooshort, Y1, Y)
        return X, Y

    quiver_doc = _quiver_doc


