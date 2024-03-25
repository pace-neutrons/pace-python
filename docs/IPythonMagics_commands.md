# IPythonMagics commands

When using Jupyter notebooks, Matlab plots by default are shown as an inline 
screenshot. This default behaviour can be edited through the use of IPyhonMagic
commands and Matlab plots can be produced as usual (displayed as windows),
as long as you are running Jupyter locally (i.e. not using a Jupyter Hub instance).
This is because otherwise the plot window would render on the Hub server
rather than the local machine.

Using the provided commands, You can specify how plots should appear: either 
'inline' [default] or 'windowed'. You can also specify how Matlab text output 
from functions appear: 'inline' [default] or 'console'

## List of commands

 - **`%matlab_plot_mode windowed`**             
windowed figures, output unchanged ('inline' default)
 - **`%matlab_plot_mode console`**              
 figure unchanged ('inline' default), console output
 - **`%matlab_plot_mode windowed console`**     
 windowed figures, console output
 - **`%matlab_plot_mode inline inline`**        
 inline figures, inline output
 - **`%matlab_plot_mode inline`**               
 inline figures, inline output
 - **`%matlab_plot_mode inline console`**       
 inline figures, console output
 - **`%matlab_plot_mode windowed inline`**  
 windowed figures, console output 

\
For inlined figures, you can also set the default figure size and resolution with

 ``` %matlab_plot_mode inline --width 400 --height 300 --resolution 150```

The values are in pixels for the width and height and dpi for resolution. A short cut:

 ``` %matlab_plot_mode inline -w 400 -h 300 -r 150```

