tol_values = {
    '1%': 96,
    '2%': 48,
    '5%': 24,
    '10%': 12
}

# I insisted on defining all values programatically "for fun" after it became more complicated than expected
# generate standard resistor values per tolerance series (base of 1 ohm)
def std_values(tolerance):
    for index in range(0, tol_values[tolerance]):
        yield 10**(index/tol_values[tolerance])

# resistor value range: 0.1 ohm to <100K ohm
resistors = {}

# as decades increase, reduce rounding precision
round_adjust = lambda r, d: r-(d+1) #if r-(d+1) >= 0 else 0

for tol in tol_values:
    if tol == '1%' or tol == '2%':
        # round to 3 places for 0.1 ohm and 1 less per decade
        resistors[tol] = [round(val*10**decade,round_adjust(3, decade)) \
                          for decade in range(-1,5) for val in std_values(tol)]
    else:
        # round to 2 places for 0.1 ohm and 1 less per decade
        resistors[tol] = [round(val*10**decade,round_adjust(2, decade)) \
                          for decade in range(-1,5) for val in std_values(tol)]

# formula-noncompliant positions to be modified
nc_pos = {
    '5%': list(range(10, 17)) + [22],   # E12 series
    '10%': list(range(5, 9)) + [11]     # E24 series
    }

# correct E12 and E24 series to the official values
for tol in ['5%', '10%']:
    for decade in range(0, 6):
        # add 0.1*base (i.e. base = 0.1, 1, 10) ohm to the first range of adjusted positons for each decade
        for i in nc_pos[tol][:-1]:
            resistors[tol][i+tol_values[tol]*decade] += 1*10**(decade-2) # adjust for 0.1 ohm as first decade
            resistors[tol][i+tol_values[tol]*decade] = \
                round(resistors[tol][i+tol_values[tol]*decade], round_adjust(2, decade-1))
        # subtract 0.1*base for last adjusted position for each decade
        resistors[tol][nc_pos[tol][-1]+tol_values[tol]*decade] -= 1*10**(decade-2)
        resistors[tol][nc_pos[tol][-1]+tol_values[tol]*decade] = \
            round(resistors[tol][nc_pos[tol][-1]+tol_values[tol]*decade], round_adjust(2, decade-1))
