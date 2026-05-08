import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # Parameters
        flat_to_flat = 40.0   # mm (distance across flats)
        thickness = 10.0      # mm extrusion height
    
        # For a regular hexagon: across-flats = sqrt(3) * circumradius * 2? (actually 2*apothem)
        # apothem = R * cos(pi/6) = R * (sqrt(3)/2)
        # across_flats = 2*apothem = R*sqrt(3)  => R = across_flats / sqrt(3)
        R = flat_to_flat / math.sqrt(3)  # circumradius (center to vertex)
        diameter = 2 * R                 # polygon() expects diameter (across vertices)
    
        result = (
            cq.Workplane("XY")
            .polygon(6, diameter)
            .extrude(thickness)
        )
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00009823/gpt_generated.stl')
