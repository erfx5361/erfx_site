import numpy as np
from app.dictionary import resistors

def parallel(ra, rb):
    return (ra * rb) / (ra + rb)

class Attenuator():

    def __init__(self, calc_mode='resistors', attenuation=float(), impedance=float(), 
                 use_standard_values=True, res_tol='1%', r1=float(), r2=float()):
        self.defined = False
        
        self.calc_mode = calc_mode

        self.z0 = float(impedance)
        self.use_standard_values = use_standard_values
        self.res_tol  = res_tol

        # if attenuation value given
        if attenuation:
            self.attenuation = float(attenuation)
        # if resistor values given
        if r1:
            self.r1 = float(r1)
            self.r2 = float(r2)

        self.outputs = {
            'r1': float(),
            'r2': float(),
            'attenuation': float(),
            'zin': float(),
            'return_loss': float()
        }

        self.outputs['power'] = {
            'r2_in': float(),
            'r1': float(),
            'r2_out': float()
        }



class Pi_Atten(Attenuator):

    def __init__(self, calc_mode='resistors', attenuation=float(), impedance=float(), 
                 use_standard_values=True, res_tol='1%', r1=float(), r2=float()):
        super().__init__(calc_mode, attenuation, impedance, 
                         use_standard_values, res_tol, r1, r2)

    
    def define_from_form(self, form):
        self.calc_mode = form.calc_mode.data
        if self.calc_mode == 'resistors':
            self.attenuation = float(form.attenuation.data)
        else:
            self.r1 = float(form.r1_input.data)
            self.r2 = float(form.r2_input.data)
        self.z0 = float(form.impedance.data)
        self.use_standard_values = form.use_standard_values.data
        self.res_tol = form.res_tol.data
        self.defined = True


    def define_output_from_form(self, form):
        # load pi-pad output values into pdiss_form
        self.outputs['r1'] = float(form.get('r1'))
        self.outputs['r2'] = float(form.get('r2'))
        self.outputs['attenuation'] = float(form.get('attenuation_output'))
        self.outputs['return_loss'] = float(form.get('return_loss'))
        self.z0 = float(form.get('impedance'))


    def pi_pad(self):
        if self.calc_mode == 'attenuation':
            self.solve_attenuation()
        else:
            self.solve_resistors()
        
        self.solve_zin()
        self.solve_return_loss()

        
    def get_pi_pad(self):
        self.pi_pad()
        return self.outputs['r1'], self.outputs['r2'], self.outputs['attenuation'], self.outputs['return_loss']


    def solve_attenuation(self):
        z0 = self.z0
        r1 = self.r1
        r2 = self.r2

        if self.use_standard_values:
            r1, r2 = get_standard_values(r1, r2, self.res_tol)
    
        # solve systems of equations 
        v1_term_1 = 1 + z0/r2 + z0/r1
        vout_term_1 = -z0/r1

        v1_term_2 = -1/r1
        vout_term_2 = 1/r1 + 1/r2 + 1/z0

        vin = 1
        voltage_coefficients = [[v1_term_1, vout_term_1], [v1_term_2, vout_term_2]]

        A = np.array(voltage_coefficients)
        B = np.array([vin, 0])

        X = np.linalg.solve(A, B)
        attenuation = round(-20*np.log10(2*X[1]/vin),2)

        self.outputs['attenuation'] = attenuation
        self.outputs['r1'] = r1
        self.outputs['r2'] = r2


    def solve_resistors(self):
        
        z0 = self.z0

        # convert attenuation in dB to linear factor a
        a = 10**(-self.attenuation/20)

        # delay rounding r1 to preserve floating point math
        r1 = z0*(1-a**2)/(2*a)

        r2 = round((a*r1) / (1 - a - (a*r1/z0)),2)
        r1 = round(r1,2)

        if self.use_standard_values:
            r1, r2 = get_standard_values(r1, r2, self.res_tol)

        self.outputs['r1'] = r1
        self.outputs['r2'] = r2
        self.outputs['attenuation'] = round(self.attenuation,2)


    def solve_zin(self):
        r1, r2 = self.outputs['r1'], self.outputs['r2']
        z0 = self.z0

        self.outputs['zin'] = parallel(parallel(z0, r2) + r1, r2)


    def solve_return_loss(self):
        zin = self.outputs['zin']
        z0 = self.z0

        self.outputs['return_loss'] = round(-20 * np.log10(abs(zin - z0) / abs(zin + z0)),2)


    def get_dissipation(self, p_in, units):
        p_in = float(p_in)
        # ensure p_in is in W
        if units == 'dBm':
            p_in = 10**(p_in/10) / 1000
        elif units == 'mW':
            p_in = p_in / 1000
        
        v_in_rms = np.sqrt(p_in*self.z0)
        a = 10**(-self.outputs['attenuation']/20)
        v_out_rms = v_in_rms*a

        i_r2_in = v_in_rms / self.outputs['r2']
        i_r1 = (v_in_rms - v_out_rms) / self.outputs['r1']
        i_r2_out = v_out_rms / self.outputs['r2']

        r2_in = round(i_r2_in**2 * self.outputs['r2'] * 1000, 2)
        r1 = round(i_r1**2 * self.outputs['r1'] * 1000, 2)
        r2_out = round(i_r2_out**2 * self.outputs['r2'] * 1000, 2)

        p_out = v_out_rms**2 / self.z0 * 1000

        return r2_in, r1, r2_out


def get_standard_values(r1, r2, res_tol):
    r1 = min(resistors[res_tol], key=lambda x: abs(x - r1))
    r2 = min(resistors[res_tol], key=lambda x: abs(x - r2))
    return r1, r2
