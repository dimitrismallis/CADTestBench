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
        # Parameters (units as given)
        height = 0.381001
        outer_d = 1.5
        hole_d = 0.060198
    
        # Outer cylinder: draw circle then positive extrude
        part = (
            cq.Workplane("XY")
            .circle(outer_d / 2.0)
            .extrude(height)
        )
    
        # Inner hole: draw smaller circle at center and negatively extrude through all
        part = (
            part
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .circle(hole_d / 2.0)
            .cutThruAll()
        )
    
        return part
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00520776/gpt_generated.stl')
