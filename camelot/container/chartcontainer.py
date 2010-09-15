from camelot.container import Container

class FigureContainer( Container ):
    """A container that is able to plot itself on a matplotlib figure canvas.
    
    Its 'plot_on_figure' method will be called in the gui thread to fill the figure
    canvas.
    
    One figure canvas can contain multiple axes (=sub plots)
    """
    
    def __init__(self, axes):
        """
        :param axes: a list of AxesContainer objects representing all the subplots, in
        the form of ::
        
          [[ax1, ax2],
           [ax3, ax4]]
           
        """
        self.axes = axes
        
    def plot_on_figure(self, fig):
        """Draw all axes (sub plots) on a figure canvas"""
        if self.axes:
            rows = len(self.axes)
            cols = len(self.axes[0])
            for i,row in enumerate(self.axes):
                for j,subplot in enumerate(row):
                    n = i*cols + j
                    ax = fig.add_subplot( rows, cols, n+1 )
                    ax.clear()
                    subplot.plot_on_axes( ax )
                
    
class AxesContainer( Container ):
    """A container that is able to generate a plot on a matplotlib axes"""
    
    def plot_on_axes(self, ax):
        pass
    
class PlotContainer( AxesContainer ):
    """A container for a simple xy plot, equivalent to the matplotlib or
    matlab plot command.
    """
    
    def __init__(self, *args):
        """:param *args: the arguments to be passed to the matplotlib plot command"""
        super(PlotContainer, self).__init__()
        self._plot_args = args
        
    def plot_on_axes(self, ax):
        ax.plot( *self._plot_args )
        super(PlotContainer, self).plot_on_axes( ax )
    
                    
def structure_to_figure_container( structure ):
    """Convert a structure to a figure container, if the structure
    is an instance of a FigureContainer, return as is.
    
    If the structure is an instance of an AxesContainer, return a
    FigureContainer with a single Axes.
    
    If the structure is a list, use the structure as a constructor
    argument for the FigureContainer
    """
    
    if isinstance(structure, FigureContainer):
        return structure
    if isinstance(structure, AxesContainer):
        return FigureContainer( [[structure]] )
    if isinstance(structure, (list, tuple)):
        return FigureContainer( structure )