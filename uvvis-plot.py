import sys
import re
import numpy as np
import matplotlib.pyplot as plt

def search_file(f_name,units):
    ''' Grabs all the oscillator strengths and excitation energies '''

    # grab poles/oscillator strengths
    osc, poles = [], []
    searchfile = open(f_name, "r")
    for line in searchfile:
        if 'Excited State' in line:
            contents = re.split('\s+|=',line)
            osc.append(float(contents[10]))
            if units == 'eV':
                poles.append(float(contents[5]))
            elif units == 'nm': 
                poles.append(float(contents[7]))
            else:
                print 'Units: %s not available' % units
                sys.exit()
    searchfile.close()

    return osc, poles

def combine_calculations(f_names,units):
    ''' Finds all the oscillator strengths and excitation energies (poles) 
        from a list of Gaussian output files
    '''

    # search each file and combine the oscillator strengths 
    # and poles into a single list
    combined_osc, combined_poles = [], []
    for f_name in f_names:
        osc, poles      = search_file(f_name,units)
        combined_poles += poles
        combined_osc   += osc

    return combined_osc, combined_poles

def broaden_spectrum(osc,poles,b_type,sigma):
    ''' Broaden poles to have a particular line shape '''

    npnts = 3000

    # define the range of frequencies
    pole_min, pole_max = min(poles)-4, max(poles)+4
    freq_step = (pole_max - pole_min) / npnts
    freq = [pole_min + i*freq_step for i in range(npnts)]

    # Build absorption spectrum by brodening each pole
    Abs = np.zeros([npnts])
    for i in range(len(osc)):
#       print 'Energy = %.4f, Osc = %.4f' % (poles[i], osc[i])
        for j in range(npnts):
            if b_type == 'lorentz':
                x       = (poles[i] - freq[j]) / (sigma/2)
                Abs[j] += osc[i] / (1 + x**2)
            else:
                print 'Broadening Scheme %s NYI' % b_type
                sys.exit()
            
    return Abs, freq

def plot_spectrum(Abs,freq,osc,poles,title,units):

    fig = plt.figure()  
    ax  = fig.gca()
    ax.plot(freq,Abs)
    ax.vlines(poles,[0],osc)
#   ax.invert_xaxis()  # sometimes helpful to invert axis if using nm
#   plt.xlim(325,500)
    plt.title(title)
    plt.xlabel('Wavelength (%s)' % units)
    plt.ylabel('Intensity (abribrary)')

if __name__ == '__main__':

    # grab oscillators and poles and broden
    broaden, sigma, units = 'lorentz', 0.2, 'eV'
    osc, poles = combine_calculations(sys.argv[1:],units)
    Abs, freqs = broaden_spectrum(osc,poles,broaden,sigma)

    # shift spectrum and plot
    shift   = 0.0 # eV
    freqs   = [freq+shift for freq in freqs] 
    poles   = [pole+shift for pole in poles] 
    title   = 'MbCO'
    plot_spectrum(Abs,freqs,osc,poles,title,units)
    plt.show()

    
