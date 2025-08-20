from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, RadioField, HiddenField
from wtforms.validators import DataRequired, NumberRange
from app import calculate
from flask import jsonify

pi_atten = calculate.Pi_Atten()

class PiPadForm(FlaskForm):

    # Common fields
    impedance = StringField('Impedance (Ω)', default='50', validators=[DataRequired()])
    use_standard_values = BooleanField('Use Standard Values', default=True)
    res_tol = SelectField('Resistor Tolerance', choices=['1%', '2%', '5%', '10%'])
    submit = SubmitField('Calculate')
    
    # Mode-specific inputs
    attenuation = StringField('Attenuation (dB)', validators=[])
    r1_input = StringField('R1 (Ω)', validators=[])
    r2_input = StringField('R2 (Ω)', validators=[])
    
    # Output fields
    r1 = StringField('R1 (Ω)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})
    r2 = StringField('R2 (Ω)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})
    attenuation_output = StringField('Attenuation (dB)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})
    return_loss = StringField('Return Loss (dB)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})

    calc_mode = RadioField(
        'Calculator Mode',
        choices=[
            ('resistors', 'Resistors'),
            ('attenuation', 'Attenuation')
        ],
        default='resistors'
    )
    # Hidden field to identify the form type
    form_type = HiddenField(default='pipad_form')


    def populate_pi_pad_form(self, pi_atten):

        if self.calc_mode.data == 'resistors':
            self.attenuation.validators = [NumberRange(min=0.001, max=1000)]
            self.r1_input.validators = []
            self.r2_input.validators = []
        else:  # attenuation mode
            self.r1_input.validators = [NumberRange(min=0.1, max=100000)]
            self.r2_input.validators = [NumberRange(min=0.1, max=100000)]
            self.attenuation.validators = []
        
        r1, r2, attenuation_output, return_loss = pi_atten.get_pi_pad()

        return jsonify({
                    'r1': r1,
                    'r2': r2,
                    'attenuation_output': attenuation_output,
                    'return_loss': return_loss
                })


class PiPadDissipationForm(FlaskForm):
    
    input_power = StringField('Input Power', validators=[DataRequired()])
    units = SelectField('Units', choices=[('mW', 'mW'), ('dBm', 'dBm')], default='dBm', validators=[DataRequired()])
    submit = SubmitField('Calculate')

    # Output fields
    power_r1 = StringField('R1 (mW)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})
    power_r2_in = StringField('R2-Input (mW)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})
    power_r2_out = StringField('R2-Output (mW)', render_kw={'readonly': True, 'class': 'form-control form-control-sm output-field'})

    # Hidden field to identify the form type
    form_type = HiddenField(default='pdiss_form')


    def populate_pi_pad_dissipation(self, pi_atten):
        power_r2_in, power_r1, power_r2_out = pi_atten.get_dissipation(self.input_power.data, \
                                                                       self.units.data)
        return jsonify({
            'power_r1': power_r1,
            'power_r2_in': power_r2_in,
            'power_r2_out': power_r2_out
        })




