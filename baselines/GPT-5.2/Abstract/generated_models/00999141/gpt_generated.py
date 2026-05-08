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
        base_angle_deg = 70.0          # base angle of the isosceles trapezium
        bottom_width = 80.0            # longer base (mm)
        top_width = 40.0               # shorter base (mm)
        thickness = 3.0                # plate thickness (mm)
    
        # Compute trapezoid height from base angle:
        # For an isosceles trapezoid, horizontal inset per side = (bottom-top)/2
        inset = (bottom_width - top_width) / 2.0
        base_angle_rad = math.radians(base_angle_deg)
        height = inset * math.tan(base_angle_rad)
    
        # Define vertices (counter-clockwise), centered about X=0
        # Bottom base at y=0, top base at y=height
        pts = [
            (-bottom_width / 2.0, 0.0),
            ( bottom_width / 2.0, 0.0),
            ( top_width / 2.0,    height),
            (-top_width / 2.0,    height),
        ]
    
        # Build and extrude
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(thickness)
        )
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00999141/gpt_generated.stl')
