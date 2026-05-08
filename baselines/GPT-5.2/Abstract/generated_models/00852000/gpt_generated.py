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
        sq_size = 60.0
        sq_height = 8.0
    
        wall = 2.0  # shell thickness (hollowing) while keeping top
    
        # Bottom center boss
        bottom_boss_d = 16.0
        bottom_boss_h = sq_height - 1.0  # slightly less than square
    
        # Top corner bosses
        corner_boss_d = 14.0  # slightly smaller than first circle
        corner_boss_h = sq_height - 2.0  # slightly less than square
        corner_offset = 10.0  # distance from each edge
    
        # --- Base square, slightly extruded ---
        base = cq.Workplane("XY").rect(sq_size, sq_size).extrude(sq_height)
    
        # --- Hollow out inside WITHOUT removing the top ---
        # Remove the bottom face and shell inward (negative thickness) -> open bottom, top intact
        hollow = base.faces("<Z").shell(-wall)
    
        # --- Bottom centered circle, extruded slightly less than the square ---
        bottom_boss = (
            cq.Workplane("XY")
            .circle(bottom_boss_d / 2.0)
            .extrude(bottom_boss_h)
        )
    
        # --- Four top circles near corners, symmetric, slightly less extruded than square ---
        pts = [
            ( sq_size/2 - corner_offset,  sq_size/2 - corner_offset),
            (-sq_size/2 + corner_offset,  sq_size/2 - corner_offset),
            (-sq_size/2 + corner_offset, -sq_size/2 + corner_offset),
            ( sq_size/2 - corner_offset, -sq_size/2 + corner_offset),
        ]
    
        top_bosses = (
            cq.Workplane("XY", origin=(0, 0, sq_height))  # start at top surface
            .pushPoints(pts)
            .circle(corner_boss_d / 2.0)
            .extrude(corner_boss_h)
        )
    
        final_result = hollow.union(bottom_boss).union(top_bosses)
        return final_result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00852000/gpt_generated.stl')
