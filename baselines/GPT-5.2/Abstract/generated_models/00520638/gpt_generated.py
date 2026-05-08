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
        height = 60.0
        stem_w = 14.0
    
        bowl_outer_r = 18.0
        bowl_inner_r = 10.0
        bowl_center_x = stem_w + bowl_outer_r * 0.55
        bowl_center_y = 42.0
    
        bridge_h = 10.0
        bridge_w = stem_w + 6.0
    
        leg_w = 10.0
        leg_len = 34.0
        leg_angle_deg = -35.0
        leg_center_x = stem_w + leg_len * 0.35
        leg_center_y = 22.0
    
        thickness = 8.0
    
        wp = cq.Workplane("XY")
    
        # Stem: rectangle defined at origin then moved so its lower-left is at (0,0)
        stem = (
            wp.rect(stem_w, height)
            .extrude(thickness)
            .translate((stem_w / 2.0, height / 2.0, thickness / 2.0))
        )
    
        # Outer bowl: cylinder
        outer_bowl = (
            wp.circle(bowl_outer_r)
            .extrude(thickness)
            .translate((bowl_center_x, bowl_center_y, thickness / 2.0))
        )
    
        # Inner bowl: cylinder to cut out
        inner_bowl = (
            wp.circle(bowl_inner_r)
            .extrude(thickness)
            .translate((bowl_center_x, bowl_center_y, thickness / 2.0))
        )
    
        # Bridge: rectangle to ensure connection
        bridge = (
            wp.rect(bridge_w, bridge_h)
            .extrude(thickness)
            .translate((bridge_w / 2.0, bowl_center_y, thickness / 2.0))
        )
    
        # Leg: rotated rectangle extruded
        leg = (
            wp.rect(leg_len, leg_w)
            .extrude(thickness)
            .rotate((0, 0, 0), (0, 0, 1), leg_angle_deg)
            .translate((leg_center_x, leg_center_y, thickness / 2.0))
        )
    
        # Combine and cut inner bowl
        result = stem.union(outer_bowl).union(bridge).union(leg).cut(inner_bowl)
    
        # Optional fillet on vertical edges
        result = result.edges("|Z").fillet(1.0)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00520638/gpt_generated.stl')
