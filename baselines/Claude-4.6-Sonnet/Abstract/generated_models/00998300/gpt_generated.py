import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        stem_width   = 10.0   # X dimension of vertical stem
        stem_height  = 40.0   # Y dimension of vertical stem
        extrude_depth = 5.0   # Z extrusion depth (same for both parts)
    
        # Crossbar: length ~1/4 of stem height = 10, same "width" (Z depth) as stem
        crossbar_length = stem_height / 4   # = 10
        crossbar_height = stem_width        # same width as stem = 10 (Y thickness of crossbar)
    
        # --- Step 1: Vertical stem ---
        # Centered at origin in XY, extruded in +Z
        # X: [-stem_width/2, stem_width/2] = [-5, 5]
        # Y: [-stem_height/2, stem_height/2] = [-20, 20]
        stem = (
            cq.Workplane("XY")
            .rect(stem_width, stem_height)
            .extrude(extrude_depth)
        )
    
        # --- Step 2: Horizontal crossbar (skewed T) ---
        # The crossbar is placed near the top of the stem.
        # "Closer to the top" → center of crossbar at Y = stem_height/2 - crossbar_height/2 = 20 - 5 = 15
        # "Skewed" → crossbar extends from stem's left edge to the right:
        #   X center of crossbar = stem_width/2 + crossbar_length/2 - stem_width/2 ... 
        #   Let's place crossbar so its left edge aligns with stem's left edge (-5)
        #   and extends right: X center = -5 + crossbar_length/2 = -5 + 5 = 0
        #   But that would be symmetric. For skewed: left edge at stem center (0), extends right to +10
        #   X center of crossbar = 0 + crossbar_length/2 = 5
        # This makes it skewed (offset to the right of the stem center)
    
        crossbar_cx = stem_width / 2 + crossbar_length / 2  # = 5 + 5 = 10 (right of stem)
        # Actually let's make it so the crossbar starts at the stem's right edge and extends further right
        # That gives a clear skewed T shape
        # crossbar left edge at x=0 (stem center), right edge at x=10
        # center at x=5 — but stem occupies x=[-5,5], so crossbar overlaps stem on right half
        # Better: crossbar left edge at x=-5 (stem left), right edge at x=5+10=15 but offset
        # Let's go with: crossbar center at x = stem_width/2 + crossbar_length/2 = 5 + 5 = 10
        # This means crossbar goes from x=5 to x=15, touching stem's right edge → skewed T
    
        crossbar_cx = stem_width / 2 + crossbar_length / 2  # = 10
        crossbar_cy = stem_height / 2 - crossbar_height / 2  # = 15 (near top)
    
        crossbar = (
            cq.Workplane("XY")
            .center(crossbar_cx, crossbar_cy)
            .rect(crossbar_length, crossbar_height)
            .extrude(extrude_depth)
        )
    
        # --- Step 3: Union stem and crossbar ---
        result = stem.union(crossbar)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # X: stem goes [-5, 5], crossbar goes [5, 15] → total X = [-5, 15] = 20
        expected_xlen = stem_width / 2 + crossbar_length + stem_width / 2  # 5 + 10 + 5 = 20
        # Wait: stem X: [-5,5], crossbar X: [10-5, 10+5] = [5, 15]
        # Combined X: [-5, 15] → xlen = 20
        assert abs(bb.xmin - (-stem_width / 2)) < TOL, f"xmin expected {-stem_width/2}, got {bb.xmin}"
        assert abs(bb.xmax - (stem_width / 2 + crossbar_length)) < TOL, f"xmax expected {stem_width/2 + crossbar_length}, got {bb.xmax}"
        assert abs(bb.xlen - (stem_width + crossbar_length)) < TOL, f"xlen expected {stem_width + crossbar_length}, got {bb.xlen}"
    
        # Y: stem goes [-20, 20], crossbar goes [10, 20] → total Y = [-20, 20] = 40
        assert abs(bb.ymin - (-stem_height / 2)) < TOL, f"ymin expected {-stem_height/2}, got {bb.ymin}"
        assert abs(bb.ymax - (stem_height / 2)) < TOL, f"ymax expected {stem_height/2}, got {bb.ymax}"
        assert abs(bb.ylen - stem_height) < TOL, f"ylen expected {stem_height}, got {bb.ylen}"
    
        # Z: both extruded by same amount
        assert abs(bb.zmin - 0) < TOL, f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_depth) < TOL, f"zmax expected {extrude_depth}, got {bb.zmax}"
        assert abs(bb.zlen - extrude_depth) < TOL, f"zlen expected {extrude_depth}, got {bb.zlen}"
    
        # Volume: stem + crossbar - overlap
        # Stem: 10 * 40 * 5 = 2000
        # Crossbar: 10 * 10 * 5 = 500
        # Overlap: crossbar touches stem at x=5 (edge), no overlap in X since crossbar starts at x=5
        # Actually crossbar X: [5, 15], stem X: [-5, 5] → they share edge at x=5, no volumetric overlap
        stem_vol = stem_width * stem_height * extrude_depth  # 2000
        crossbar_vol = crossbar_length * crossbar_height * extrude_depth  # 500
        # No overlap (they share only a face at x=5)
        expected_vol = stem_vol + crossbar_vol  # 2500
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Crossbar is near the top: crossbar Y center at 15, stem Y center at 0
        # The crossbar Y range [10, 20] is within stem Y range [-20, 20] → connected
        # Verify the object is a single solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Verify crossbar is near top: center of mass should be above stem center (Y > 0)
        com = cq.Shape.centerOfMass(result.val())
        assert com.y > 0, f"Center of mass Y should be positive (crossbar near top), got {com.y}"
    
        # Verify skewed: center of mass X should be positive (crossbar extends to the right)
        assert com.x > 0, f"Center of mass X should be positive (skewed right), got {com.x}"
    
        print(f"Bounding box: X=[{bb.xmin:.2f},{bb.xmax:.2f}], Y=[{bb.ymin:.2f},{bb.ymax:.2f}], Z=[{bb.zmin:.2f},{bb.zmax:.2f}]")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998300/gpt_generated.stl')
