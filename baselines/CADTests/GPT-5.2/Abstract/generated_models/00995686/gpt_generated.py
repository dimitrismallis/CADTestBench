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
        outer_r = 20.0
        wall = 3.0
        inner_r = outer_r - wall
        height = 40.0
    
        # Sector to remove (degrees). Example: remove 90° of the pipe.
        cut_angle = 90.0
        # Center angle of the removed sector (degrees). 0° points along +X.
        cut_center = 0.0
    
        # --- Base: hollow cylinder (pipe) ---
        pipe = (
            cq.Workplane("XY")
            .circle(outer_r)
            .circle(inner_r)
            .extrude(height)
        )
    
        # --- Build a "sector" cutter as an annular sector extruded through height ---
        a0 = math.radians(cut_center - cut_angle / 2.0)
        a1 = math.radians(cut_center + cut_angle / 2.0)
    
        # Points on outer arc
        p0o = (outer_r * math.cos(a0), outer_r * math.sin(a0))
        p1o = (outer_r * math.cos(a1), outer_r * math.sin(a1))
    
        # Points on inner arc
        p0i = (inner_r * math.cos(a0), inner_r * math.sin(a0))
        p1i = (inner_r * math.cos(a1), inner_r * math.sin(a1))
    
        # Create a closed wire for the annular sector:
        # outer arc (a0->a1), radial line to inner, inner arc (a1->a0), radial line back to start
        sector_wire = (
            cq.Workplane("XY")
            .moveTo(*p0o)
            .radiusArc(p1o, outer_r)     # outer arc
            .lineTo(*p1i)                # radial line inward
            .radiusArc(p0i, inner_r)     # inner arc back
            .close()
        )
    
        sector_cutter = sector_wire.extrude(height)
    
        # --- Cut the sector out of the pipe ---
        result = pipe.cut(sector_cutter)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00995686/gpt_generated.stl')
