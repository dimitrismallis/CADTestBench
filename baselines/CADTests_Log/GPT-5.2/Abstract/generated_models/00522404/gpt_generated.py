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
        # Parameters (mm)
        square_size = 40.0          # square side length (X and Z)
        base_thickness = 6.0        # small extrusion along Y for the base
        pillar_width = square_size * 0.5  # about half the square width (in Z)
        pillar_height = 160.0       # very large extrusion along Y for the pillar
    
        # Base: square on XZ plane, extruded along +Y
        base = (
            cq.Workplane("XZ")
            .rect(square_size, square_size)
            .extrude(base_thickness)  # extrudes normal to XZ, i.e., along +Y
        )
    
        # Pillar: rectangle centered on same location, same X length, half Z width
        pillar = (
            base
            .faces(">Y").workplane(centerOption="CenterOfMass")
            .rect(square_size, pillar_width)
            .extrude(pillar_height)
        )
    
        return pillar
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00522404/gpt_generated.stl')
