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
        # Input points (in meters, as provided)
        pts_m = [
            (-0.05430806,  0.05735744),
            (-0.05430806, -0.05851911),
            (-0.04704762, -0.05851911),
            (-0.03833510, -0.00217813),
            ( 0.00232334, -0.00217813),
            ( 0.01161670, -0.06200412),
            ( 0.01742505, -0.06200412),
            ( 0.01452087,  0.01030982),
            (-0.02875133,  0.01030982),
            (-0.04501470,  0.05735744),
            (-0.05430806,  0.05735744),
        ]
    
        # CadQuery default units are mm; convert meters -> mm
        m_to_mm = 1000.0
        pts = [(x * m_to_mm, y * m_to_mm) for x, y in pts_m]
    
        extrude_m = 0.1016
        extrude_mm = extrude_m * m_to_mm
    
        scale_factor = 7.38186180173805
    
        # Build the "h" profile, close it, and extrude
        bench = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_mm)
        )
    
        # Scale uniformly about origin, then rotate about X and Z axes
        bench = bench.val().scale(scale_factor)
        bench = bench.rotate((0, 0, 0), (1, 0, 0), -90)
        bench = bench.rotate((0, 0, 0), (0, 0, 1), -90)
    
        return cq.Workplane("XY").newObject([bench])
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00037135/gpt_generated.stl')
