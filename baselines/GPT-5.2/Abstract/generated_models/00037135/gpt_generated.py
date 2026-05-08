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
        # --- Parameters (mm) ---
        height_2d = 120.0          # overall height of the 'h' sketch in Y
        leg_w = 25.0               # thickness of each vertical leg in X
        gap = 60.0                 # clear gap between inner faces of legs
        crossbar_h = 25.0          # thickness of the crossbar in Y (in Y direction)
        bench_thickness = 30.0     # extrusion height in Z
        edge_fillet = 2.0
    
        # Derived overall width of the 'h'
        total_w = 2 * leg_w + gap
    
        # The "h" can be made as: outer rectangle minus two inner rectangles (top and bottom voids)
        # Inner void width is the gap between legs; inner void height is (height_2d - crossbar_h)/2
        void_h = (height_2d - crossbar_h) / 2.0
        if void_h <= 0:
            raise ValueError("crossbar_h must be smaller than height_2d")
    
        # Centers of the top and bottom void rectangles
        top_void_y = (crossbar_h / 2.0) + (void_h / 2.0)
        bot_void_y = -top_void_y
    
        h_face = (
            cq.Workplane("XY")
            # outer boundary
            .rect(total_w, height_2d)
            # subtract top void
            .rect(gap, void_h, forConstruction=False)
            .center(0, top_void_y)
            .rect(gap, void_h)
            .center(0, -top_void_y)  # move back down past origin to bottom void center
            .rect(gap, void_h)
        )
    
        # The above created multiple wires; use a single face by extruding with "cut" via regions:
        # Easiest robust approach: make outer solid then cut the two void solids.
        outer = cq.Workplane("XY").rect(total_w, height_2d).extrude(bench_thickness)
    
        voids = (
            cq.Workplane("XY")
            .center(0, top_void_y).rect(gap, void_h).extrude(bench_thickness)
            .union(
                cq.Workplane("XY").center(0, bot_void_y).rect(gap, void_h).extrude(bench_thickness)
            )
        )
    
        bench = outer.cut(voids)
    
        if edge_fillet and edge_fillet > 0:
            bench = bench.edges("|Z").fillet(edge_fillet)
    
        return bench
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00037135/gpt_generated.stl')
