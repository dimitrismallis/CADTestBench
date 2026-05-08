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
        # --- Parameters ---
        # Across-flats / circumscribed diameters for polygons (CadQuery polygon uses circumscribed diameter)
        d1 = 60.0  # base hex diameter
        d2 = 42.0  # 2nd hex diameter
        d3 = 28.0  # 3rd hex diameter
        d4 = 22.0  # triangle diameter
    
        h1 = 6.0   # base extrude
        h2 = 4.5   # slightly less
        h3 = 3.2   # slightly less
        h4 = 2.2   # slightly less
    
        # Rotations to avoid vertex alignment between stacked shapes
        a1 = 0.0
        a2 = 15.0
        a3 = 30.0
        a4 = 10.0
    
        # --- Model ---
        result = (
            cq.Workplane("XY")
            # 1) Base hexagon
            .polygon(6, d1).extrude(h1)
            # 2) Smaller hexagon on top, rotated
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .transformed(rotate=cq.Vector(0, 0, a2 - a1))
            .polygon(6, d2).extrude(h2)
            # 3) Third smaller hexagon on top, rotated again
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .transformed(rotate=cq.Vector(0, 0, a3 - a2))
            .polygon(6, d3).extrude(h3)
            # 4) Triangle on top, rotated (and different vertex count helps avoid alignment too)
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .transformed(rotate=cq.Vector(0, 0, a4 - a3))
            .polygon(3, d4).extrude(h4)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00853706/gpt_generated.stl')
