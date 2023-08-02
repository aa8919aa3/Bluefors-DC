# Bluefors-DC

This is a repository for codes performing various kinds of DC measurements in LabVIEW that I wrote during my Ph.D. for automating data collection and analysis of the Bluefors LD-400 system in my lab. The control electronics used are as follows:

1) Magnet controller - AMI 430 (2-axis controller)
2) Temperature controller - Lakeshore 372

## Please note that there are no interlocks for the magnet ramp rate and the heat applied to the mixing chamber plate for temperature control ##
## Do take care NOT to exceed the rates/limits recommended during installation ##

The measurement electronics were used to measure current-voltage characteristics and voltage as a function of temperature and 2D magnetic field. The electronics used for the measurements are:

1) Keithley 6221 Current source (K6221)
2) Keithley 2182A Nanovoltmeter (K2182A)
3) Keithley 2636B Dual voltage source (K3636B)
4) Zurich Instructruments MFLI (MFLI)

The LabVIEW drivers for these instruments and relevant subVIs are also attached to this repository.
