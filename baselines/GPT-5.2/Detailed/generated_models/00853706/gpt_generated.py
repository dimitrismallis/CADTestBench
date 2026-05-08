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
        # --- Parameters (units as given) ---
        s1, h1 = 1.15342, 0.249723
        s2, h2 = 0.865066, 0.199778
        s3, h3 = 0.576711, 0.099889
    
        # Triangle "effective radius" given ~0.228054 (treat as circumradius)
        tri_R = 0.228054
        h4 = 0.079911
    
        # --- Helper: regular n-gon by side length (uses circumradius) ---
        # For a regular n-gon: side s = 2*R*sin(pi/n)  => R = s/(2*sin(pi/n))
        def ngon_diameter_from_side(n: int, side: float) -> float:
            R = side / (2.0 * math.sin(math.pi / n))
            return 2.0 * R  # CadQuery polygon() takes circumscribed diameter
    
        # Hexagon: for n=6, R = s, so diameter = 2*s (but keep generic)
        d1 = ngon_diameter_from_side(6, s1)
        d2 = ngon_diameter_from_side(6, s2)
        d3 = ngon_diameter_from_side(6, s3)
    
        # Triangle: use provided effective radius as circumradius directly
        d4 = 2.0 * tri_R
    
        # Small rotations (degrees) to avoid vertex alignment between tiers
        a1 = 7.0
        a2 = 19.0
        a3 = 33.0
        a4 = 11.0
    
        # --- Build model ---
        result = (
            cq.Workplane("XY")
            .polygon(6, d1)
            .rotate((0, 0, 0), (0, 0, 1), a1)
            .extrude(h1)
    
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .polygon(6, d2)
            .rotate((0, 0, 0), (0, 0, 1), a2)
            .extrude(h2)
    
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .polygon(6, d3)
            .rotate((0, 0, 0), (0, 0, 1), a3)
            .extrude(h3)
    
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .polygon(3, d4)
            .rotate((0, 0, 0), (0, 0, 1), a4)
            .extrude(h4)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00853706/gpt_generated.stl')
