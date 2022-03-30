# Prepare ETD Light Curves for analysis in AIJ
This code has been written hastily in order to prepare the light curves downloaded from Exoplanet Transit Database (ETD) to be analyzed in AstroImageJ (AIJ) by converting the column that keeps time to BJD-TDB format, computing the AIRMASS based on the location of the observers and the coordinates of the object and printing an output file that will be used in the analysis with AIJ.

Since ETD light curves have been acquired by amateur observers, they ignore airmass-detrending, which improves the precision of mid-transit times measured from those light curves. So this small code-snippet was coded in Python (hosted in this Jupyter notebook) to convert the light curves in ETD to BJD-TDB time scale, compute the airmass.

The information on how to use the code is explained in detail within the Jupyter notebook version of the code. The code has been provided especially to the observers & researchers working in the project titled "Exoplanet Discovery with the Timing Technique" funded by TUBITAK with the project number 118F042. However, anyone interested in the code are welcome to use it and provide feedback. Nevertheless, the code has no error-handling unfortunately. So you are at your own risk. You have to enter the information correctly. Otherwise it crashes! If an unexpected error occur please let us know and we will correct the code if the error is some bug or direct you otherwise.

#[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ozbasturk/prepare_etd_lc_for_aij/master)
