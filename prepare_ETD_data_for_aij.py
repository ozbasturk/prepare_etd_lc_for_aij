from astropy import time, coordinates as coord, units as u
import pandas as pd
import numpy as np
import os
# Get the name of the light curve file
filename = input("Enter the name of the light curve data file: \n")
print()

# We need a separator
separator = input("Please enter the delimiter used to separate the columns in your file. Enter 't' if your file is tab delimited, 's' if space delimited without single quotes: \n")
if separator == 't':
    separator = '\t'
elif separator == 's':
    separator = ' '
print()

# Create the data frame and show the light curve
lc = pd.read_csv(filename, sep=separator, skipinitialspace=True)
print("Your light curve is: ")
print(lc.head())
print()

# Ask which column is which
jdcol = input("Which column keeps your time in JD?\n")
flux = input("Which column keeps your flux (or magnitude)?\n")
fluxerr = input(
    "Which column keeps your flux (or magnitude) errors? If it is not in your file then hit <enter>\n")
print()

# Which reference frames are your timings in (JD, HJD or BJD) in UTC
jdtype = input("What is the reference frame for the timings reported in UTC scale Please enter 'JD' for geocentric, 'HJD' for heliocentric, 'BJD' for barycentric values?: \n")
print()

# If the scale is already dynamical (TDB) or in UTC
jdscale = 'UTC'
jdscale = input(
    "What is the scale of the timings reported in. Please enter 'TDB' if the timings are dynamical or 'UTC' if they are not: \n")

# Remove outliers
# Discarding criteria is 5*sigma
mu = lc[flux].mean()
sigma = lc[flux].std()
llim = mu - 5*sigma
ulim = mu + 5*sigma
# index of the points out of the limits
index2drop = lc[(lc[flux] > ulim) | (lc[flux] < llim)].index
lc.drop(index2drop, inplace=True)

# if error column is empty, calculate standard deviation of
# first 5 and last 5 points and use it for all as a fudge factor
# exofast already weighs these equally
if fluxerr == '':
    series4std = pd.concat([lc[flux][:5], lc[flux][-6:]])
    fluxstd = series4std.std()
    fluxerr = flux + '_err'
    lc[fluxerr] = fluxstd*np.ones(len(lc[flux]))

try:
    hoststar = input(
        "Please enter the name of the host star as is given in Simbad: \n")
    star_coords = coord.SkyCoord.from_name(hoststar)
except:
    RA = input(
        "Please enter the right ascension of your star in hh mm ss.s format: \n")
    DEC = input(
        "Please enter the declination of your star in dd mm ss.s format: \n")
    star_coords = coord.SkyCoord(RA, DEC, frame='icrs',
                                 unit=(u.hourangle, u.deg), equinox="J2000")

# Now let us determine the location of the observer
print("The observatories in our database are \n")
print("Please be patient, this may take some time...\n")
print(coord.EarthLocation.get_site_names())
observatory = input(
    "Please enter the name of the observatory. If your observatory is not in the list hit <enter>\n")
if observatory == '':
    observatory_address = input(
        "Try entering the address of the observatory look for its coordinates in Google Earth: \n")
    if observatory_address == '':
        obslong = float(input(
            "Please enter the longitude of the observatory in d.ddd format (east is positive): \n"))
        obslat = float(input(
            "Please enter the latitude of the observatory in dd.dddd format (north is positive): \n"))
        obsalt = float(input(
            "Please enter the altitude of the observatory in meters (if not known enter 0): \n"))
        obsloc = coord.EarthLocation(
            lat=obslat*u.deg, lon=obslong*u.deg, height=obsalt*u.m)
    else:
        try:
            obsloc = coord.EarthLocation.of_site(observatory_address)
        except:
            print("The address you have entered can not be found in Google Earth!")
            obslong = float(input(
                "Please enter the longitude of the observatory in d.ddd format (east is positive): \n"))
            obslat = float(input(
                "Please enter the latitude of the observatory in dd.dddd format (north is positive): \n"))
            obsalt = float(input(
                "Please enter the altitude of the observatory in meters (if not known enter 0): \n"))
            obsloc = coord.EarthLocation(
                lat=obslat*u.deg, lon=obslong*u.deg, height=obsalt*u.m)
else:
    obsloc = coord.EarthLocation.of_site(observatory)

# make sure they are numeric
lc[jdcol] = pd.to_numeric(lc[jdcol]).astype(float)
lc[flux] = pd.to_numeric(lc[flux]).astype(float)
lc[fluxerr] = pd.to_numeric(lc[fluxerr]).astype(float)

times = time.Time(lc[jdcol], format='jd', scale='utc', location=obsloc)

# Cacluate bbarycentric or heliocentric time difference
# converts UTC to BJD and add ltt diffrence
if jdtype == "JD":
    ltt_bary = times.light_travel_time(star_coords)
elif jdtype == 'HJD':
    ltt_helio = times.light_travel_time(star_coords, 'heliocentric')
    times -= ltt_helio
    ltt_bary = times.light_travel_time(star_coords)
elif jdtype == 'BJD':
    ltt_bary = 0.
else:
    print("Your timing frame is not recognized")
    os.exit()
if jdscale == 'TDB':
    time_barycentre = ltt_bary
else:
    time_barycentre = times.tdb + ltt_bary
bjd_tdb = time_barycentre.value
times_bjd_tdb = time.Time(bjd_tdb, format='jd', scale='tdb')
lc['BJD-TDB'] = times_bjd_tdb

# Calculate the altitude / azimuth coordinates for the object
altaz = star_coords.transform_to(coord.AltAz(
    obstime=times_bjd_tdb, location=obsloc))
# and zenith angle
secz = 1 / np.cos(altaz.zen)
# to determine the airmass from Hardie (1962)
X = secz - 0.0018167*(secz - 1) - 0.002875 * \
    (secz - 1)**2 - 0.0008083*(secz - 1)**3
lc['airmass'] = X

# dump the data in pandas dataframe lc to a new file
# First find the index of the last '.' character where the extension starts
indext = len(filename) - filename[-1::-1].find('.') - 1
file2wr = filename[:indext]+'_converted.dat'
lc = lc.sort_values(['BJD-TDB'])
lc.to_csv(file2wr, sep='\t',
          float_format='%.6f',
          columns=['BJD-TDB', flux, fluxerr, 'airmass'],
          index=False)
print("Your file has been sucessfully written")
