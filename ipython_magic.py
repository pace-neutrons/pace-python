from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, line_cell_magic
from IPython.display import Image

import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

@magics_class
class MatlabMagic(Magics):
    """Call this magic using %%matlab
    All variables assigned within the cell will be available in
    Python.

    All transplantable variables assingned in Python will be
    available in this cell.
    If you need to restart matlab, use %restart_matlab
    """

    def __init__(self, shell):
        super(MatlabMagic, self).__init__(shell)
        from pySpinW import Matlab
        self.m = Matlab()

    @line_magic
    def showPlot(self, line):
        self.m.interface.set(0., 'defaultfigurevisible', 'on', nargout=0)
        self.m.interface.set(0., 'defaultfigurepaperpositionmode', 'manual', nargout=0)
        # TODO make these parameters. Quick and dirty test....
        width = 800
        height = 600
        resolution = 150
        self.m.interface.set(0., 'defaultfigurepaperposition',
        self.m.pyMatlab.double([0, 0, width / resolution, height / resolution]), nargout=0)
        self.m.interface.set(0., 'defaultfigurepaperunits', 'inches', nargout=0)
        format = 'png'
        nfig = len(self.m.interface.get(0., "children"))
        if nfig:
            with TemporaryDirectory() as tmpdir:
                try:
                    self.m.interface.eval(
                        "arrayfun("
                        "@(h, i) print(h, sprintf('{}/%i', i), '-d{}', '-r{}'),"
                        "get(0, 'children'), (1:{})')".format(
                            '/'.join(tmpdir.split(os.sep)), format, resolution,
                            nfig),
                        nargout=0)
                    self.m.interface.eval(
                        "arrayfun(@(h) close(h), get(0, 'children'))",
                        nargout=0)
                    for fname in sorted(os.listdir(tmpdir)):
                        # TODO this only returns one image. Must do better...
                        return Image(filename="{}/{}".format(tmpdir, fname))
                except Exception as exc:
                    self.Error(exc)

    @line_magic
    def getProcess(self, line):
        return self.m

    @line_magic
    def restart_matlab(self, line):
        from pySpinW import Matlab
        self.m = Matlab()


def load_ipython_extension(ipython):
    """
    Load this magic by running %load_ext transplant_magic
    """
    ipython.register_magics(MatlabMagic)