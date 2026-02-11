import numpy as np

def calculate_cross_section_area(outer_diameter, inner_diameter):
    return (np.pi / 4) * (outer_diameter**2 - inner_diameter**2)

def calculate_moment_of_inertia(outer_diameter, inner_diameter):
    return (np.pi * (outer_diameter**4 - inner_diameter**4)) / 32

def calculate_internal_diameter(outer_diameter, wall_thickness):
    return outer_diameter - (2*wall_thickness)

def calculate_max_tension(area, yield_strength, torque, outer_diameter, inertia):
    denominator = 0.09167 * inertia
    numerator = torque * outer_diameter
    under_root = yield_strength**2 - (numerator/denominator)**2
    under_root = np.maximum(under_root, 0)
    return area * np.sqrt(under_root)
    
def apply_safety_factor(safety_factor, tension):
    return (1 - safety_factor / 100) * tension