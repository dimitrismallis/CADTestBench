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
        extrude_depth = 20.0
        stem_w = 15.0        # width of the vertical stem
        total_h = 100.0      # total height of the R
        bowl_center_y = 72.0 # y-center of the bowl semicircle
        bowl_r = 28.0        # radius of the bowl
        # Bowl top = bowl_center_y + bowl_r = 100 (top of R)
        # Bowl bottom = bowl_center_y - bowl_r = 44
        bowl_top_y = bowl_center_y + bowl_r    # = 100
        bowl_bot_y = bowl_center_y - bowl_r    # = 44
        inner_bowl_r = bowl_r - stem_w         # = 13
        leg_end_x = 58.0     # x at bottom of leg
        leg_end_y = 0.0
    
        # --- Step 1: Build the "R" profile as a closed 2D wire ---
        # We trace the outer boundary of the R letter clockwise (or CCW),
        # starting from bottom-left corner (0, 0).
        #
        # The R shape:
        #   - Outer stem left edge: (0,0) -> (0, total_h)
        #   - Top of stem to bowl outer arc start: (0, total_h) -> (stem_w, total_h)
        #     Actually the bowl outer arc goes from (stem_w, bowl_top_y) around to (stem_w, bowl_bot_y)
        #   - Outer bowl arc (right semicircle): from top-right of stem to bottom-right of bowl
        #   - Junction horizontal: (stem_w, bowl_bot_y) -> inner notch
        #   - Inner bowl arc (smaller): traces back
        #   - Leg diagonal: from junction down to bottom-right
        #   - Bottom edge back to start
    
        # Let me use a simpler, cleaner approach with explicit coordinates
        # R profile points (CCW winding):
    
        # Key coordinates:
        # Bowl outer arc: center=(stem_w, bowl_center_y), radius=bowl_r
        #   starts at (stem_w, bowl_top_y) = (15, 100) going right
        #   ends at (stem_w, bowl_bot_y) = (15, 44)
        # Bowl inner arc: center=(stem_w, bowl_center_y), radius=inner_bowl_r
        #   starts at (stem_w, bowl_center_y + inner_bowl_r) = (15, 57)
        #   ends at (stem_w, bowl_center_y - inner_bowl_r) = (15, 59)... 
        # Wait, let me recalculate inner arc
        # inner arc: center=(stem_w, bowl_center_y), radius=inner_bowl_r=13
        #   top point: (stem_w, bowl_center_y + inner_bowl_r) = (15, 85)
        #   bottom point: (stem_w, bowl_center_y - inner_bowl_r) = (15, 59)
    
        # The R profile (tracing CCW from bottom-left):
        # 1. (0, 0) -> (0, 100)  : left edge of stem going up
        # 2. (0, 100) -> (15, 100) : top of stem going right  
        # 3. Outer bowl arc from (15, 100) around right side to (15, 44)
        #    Arc center = (15, 72), radius=28, going clockwise (right side)
        #    Midpoint of arc = (15+28, 72) = (43, 72)
        # 4. (15, 44) -> (15, 59) : short vertical up to inner arc bottom
        # 5. Inner bowl arc from (15, 59) around right side back to (15, 85)
        #    Arc center = (15, 72), radius=13, going counter-clockwise
        #    Midpoint = (15+13, 72) = (28, 72)
        # 6. (15, 85) -> (15, 100): up to close... wait this doesn't work
    
        # Let me redesign more carefully.
        # The R has:
        # - Outer contour: stem left, top, outer bowl arc, leg diagonal, bottom
        # - Inner contour (hole): inner bowl arc forms a closed loop (the eye of R)
    
        # Actually for a solid R, I'll trace the full outline as one closed path
        # with the bowl being a bump (not a hole through the letter).
    
        # Simpler approach: trace the R outline as a single closed polygon+arc path
    
        # R outline (no inner hole, solid letter):
        # Start at (0, 0), go CCW:
        # Bottom: (0,0) -> (leg_end_x, 0)  [bottom edge]
        # Leg right side: (leg_end_x, 0) -> (stem_w + bowl_r, bowl_bot_y)  [leg outer edge going up-left]
        # Bowl outer arc bottom to top: arc from (stem_w + bowl_r, bowl_bot_y) ... 
        # Hmm, this is getting complex. Let me use a different decomposition.
    
        # CLEAN APPROACH: Build R as union of:
        # 1. Vertical stem rectangle
        # 2. Bowl (half-annulus) on upper right  
        # 3. Leg (trapezoid/parallelogram) on lower right
        # Then extrude the 2D union
    
        # Actually, let me just draw the full R outline as a wire with lines and arcs
        # using the Workplane 2D drawing tools.
    
        # R dimensions:
        # - Height: 100, stem_w: 15
        # - Bowl: outer radius 28, inner radius 13, center at (15, 72)
        # - Bowl spans from y=44 to y=100 on the left side (x=15)
        # - Leg: from (15, 44) to (58, 0) on outer, from (15, 59) to (35, 0) on inner
    
        # Trace the OUTER boundary of R (single closed wire, CCW):
        # P0=(0,0) -> P1=(0,100) [left stem edge, going up]
        # P1=(0,100) -> P2=(15,100) [top of stem, going right] -- actually top goes to arc start
        # Arc outer bowl: from (15,100) CW around to (15,44), midpoint=(43,72)
        # P3=(15,44) -> P4=(35,0) [inner leg edge, going down-right]  
        # P4=(35,0) -> P5=(58,0) [bottom edge, going right]
        # P5=(58,0) -> P6=(15,44) ... wait that's going back
    
        # Let me think of R differently:
        # The R letter outline (single closed path):
        # Going CCW from (0,0):
        # 1. Up left stem: (0,0) -> (0,100)
        # 2. Right along top: (0,100) -> (15,100)  [but this is where outer arc starts]
        # 3. Outer bowl arc CW: (15,100) -> midpoint(43,72) -> (15,44)
        # 4. Right along junction: (15,44) -> (28,44)  [horizontal to leg start]
        # 5. Leg outer edge: (28,44) -> (58,0)
        # 6. Bottom right to left: (58,0) -> (35,0)
        # 7. Leg inner edge: (35,0) -> (15+13, 44+?) ... 
    
        # This is getting complicated. Let me use a much simpler approach:
        # Build R from basic shapes using boolean union in 2D (Sketch API)
    
        # FINAL APPROACH: Use Sketch API with rectangles, circles, and boolean ops
    
        # Step 1: Full bounding rectangle (stem height)
        # Step 2: Add bowl (circle sector) 
        # Step 3: Subtract inner bowl
        # Step 4: Add leg
        # Step 5: Subtract areas that aren't part of R
    
        # Even simpler: draw R as explicit closed wire with known coordinates
    
        # Let me define all vertices of the R outline precisely:
        # The R has an outer contour and an inner contour (the bowl hole)
    
        # OUTER contour (CCW):
        # A=(0,0), B=(35,0), C=(58,0) -- bottom
        # Going up the leg outer: C=(58,0) -> D=(28,44)
        # Outer bowl arc from D=(28,44) going right/up to E=(28,100)
        #   center=(0,72), radius=28... no
    
        # Let me restart with a clean, well-defined R:
        # Stem: x=[0,15], y=[0,100]  (15 wide, 100 tall)
        # Bowl outer: semicircle on right of stem top half
        #   Center = (15, 75), outer_r = 25 -> top=(15,100), right=(40,75), bottom=(15,50)
        # Bowl inner: 
        #   Center = (15, 75), inner_r = 10 -> top=(15,85), right=(25,75), bottom=(15,65)
        # Leg: from (15,50) to (55,0) outer, from (15,65) to (30,0) inner
    
        stem_w = 15.0
        total_h = 100.0
        bowl_cx = 15.0   # bowl center x (at right edge of stem)
        bowl_cy = 75.0   # bowl center y
        outer_r = 25.0   # outer bowl radius
        inner_r = 10.0   # inner bowl radius (hole in bowl)
    
        # Key points:
        # Bowl outer arc: from (15, 100) CW to (15, 50), midpoint at (40, 75)
        # Bowl inner arc: from (15, 85) CCW to (15, 65), midpoint at (25, 75)
        # Leg outer: from (15, 50) to (55, 0)
        # Leg inner: from (15, 65) to (30, 0)
    
        leg_ox, leg_oy = 55.0, 0.0   # outer leg bottom
        leg_ix, leg_iy = 30.0, 0.0   # inner leg bottom
    
        # Full R outline as two separate closed wires:
        # Wire 1 (outer boundary of R):
        #   (0,0) -> (0,100) -> arc_outer -> (15,50) -> (55,0) -> (0,0)
        # Wire 2 (inner bowl hole):
        #   (15,65) -> arc_inner -> (15,85) -> (15,65)  -- this is the bowl eye
    
        # Actually for a solid R (no through-hole), the bowl is a bump not a hole.
        # The "eye" of the R is enclosed within the letter body.
        # So the R outline is ONE closed wire that goes:
        # outer stem -> top -> outer bowl arc -> junction -> leg outer -> bottom -> leg inner -> inner bowl arc -> back up stem inner -> close
    
        # Let me trace it carefully:
        # Start at (0,0), going CCW (standard math orientation):
        # 1. (0,0) -> (0,100): up left edge of stem
        # 2. (0,100) -> (15,100): right along top (to outer arc start)
        # 3. Outer bowl arc CW from (15,100) to (15,50): 
        #    This is a semicircle, center=(15,75), r=25
        #    Going clockwise (right side), midpoint = (40, 75)
        # 4. (15,50) -> (55,0): leg outer diagonal going down-right
        # 5. (55,0) -> (30,0): bottom going left
        # 6. (30,0) -> (15,65): leg inner diagonal going up-left
        # 7. Inner bowl arc CCW from (15,65) to (15,85):
        #    Center=(15,75), r=10, going CCW (right side)
        #    Midpoint = (25, 75)
        # 8. (15,85) -> (15,100): up to close... wait, (15,100) is already visited
        #    Actually: (15,85) -> (15,100) would overlap with step 2
        #    
        # Hmm, the inner arc connects back to the stem. Let me reconsider.
        # 
        # The R letter: the stem goes full height. The bowl is attached to the right
        # side of the stem in the upper half. The leg goes from the bottom of the bowl
        # diagonally to the bottom right.
        #
        # The INNER edge of the R (the part that makes it look like R not P):
        # After the inner bowl arc ends at (15,85), we need to go back to (0,100)?
        # No - (15,85) is INSIDE the stem area.
        #
        # I think the correct trace is:
        # The R has the stem as a solid rectangle, and the bowl as a bump.
        # The inner contour of the bowl creates the "eye" shape.
        # 
        # For a SOLID R (filled letter), the outline is:
        # Outer: left edge up, top, outer arc down, leg out, bottom back
        # Inner: the bowl eye is a separate hole (inner wire)
        #
        # So the R is: outer_wire - inner_bowl_wire
        # This gives the characteristic R shape with the enclosed eye.
    
        # Let me build this using Sketch API with boolean subtraction:
    
        # Step 1: Create the outer R shape (P shape + leg)
        # Step 2: Subtract the inner bowl to create the eye
    
        # Outer R shape = stem + outer bowl bump + leg
        # I'll build this as a closed wire:
    
        # Outer wire trace (CCW):
        # (0,0) -> (0,100) -> (15,100) 
        # -> outer arc CW to (15,50) [midpoint (40,75)]
        # -> (55,0) -> (0,0)
    
        # Inner bowl wire (the eye, CW for hole):
        # (15,65) -> inner arc CCW to (15,85) [midpoint (25,75)]
        # -> (15,65) ... this is just the arc, need to close it
        # Actually the eye is just the semicircular region:
        # (15,65) -> (15,85) via inner arc (right side), closed by the stem left edge
        # But the stem is solid, so the eye is bounded by:
        # - Left: x=15 (right edge of stem, which is also left edge of bowl)
        # - Right: inner arc
        # So the eye hole is: from (15,65) straight up to (15,85), then arc back
    
        # Inner eye wire (CCW for hole when viewed from front):
        # (15,65) -> (15,85): straight line up (along stem right edge)
        # (15,85) -> arc CCW back to (15,65): inner bowl arc going right
        # midpoint of inner arc = (25, 75)
    
        # Now let me implement this:
    
        # --- Step 1: Build outer R profile ---
        # Using Workplane 2D drawing
    
        # Outer arc: center=(15,75), r=25, from (15,100) CW to (15,50)
        # The midpoint of this CW arc (going right) is at (40, 75)
        outer_arc_mid = (bowl_cx + outer_r, bowl_cy)  # (40, 75)
    
        # Inner arc: center=(15,75), r=10, from (15,65) CCW to (15,85)  
        # Going right (CCW when viewed from +Z), midpoint at (25, 75)
        inner_arc_mid = (bowl_cx + inner_r, bowl_cy)  # (25, 75)
    
        # Build outer profile wire
        outer_wire = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(0, total_h)           # left edge up
            .lineTo(bowl_cx, total_h)     # top of stem right (15, 100)
            .threePointArc(outer_arc_mid, (bowl_cx, bowl_cy - outer_r))  # arc to (15, 50)
            .lineTo(leg_ox, leg_oy)       # leg outer diagonal to (55, 0)
            .close()                      # back to (0, 0)
        )
    
        # Build inner eye wire (the bowl hole)
        inner_wire = (
            cq.Workplane("XY")
            .moveTo(bowl_cx, bowl_cy - inner_r)   # (15, 65)
            .lineTo(bowl_cx, bowl_cy + inner_r)   # (15, 85) straight up
            .threePointArc(inner_arc_mid, (bowl_cx, bowl_cy - inner_r))  # arc back
            .close()
        )
    
        # --- Step 2: Extrude outer wire ---
        r_outer = outer_wire.extrude(extrude_depth)
    
        # --- Step 3: Subtract inner eye ---
        r_inner_cut = inner_wire.extrude(extrude_depth)
        result = r_outer.cut(r_inner_cut)
    
        # --- Final object verification ---
        TOL = 0.5
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xmin) < TOL, f"xmin expected ~0, got {bb.xmin}"
        assert abs(bb.ymin) < TOL, f"ymin expected ~0, got {bb.ymin}"
        assert abs(bb.zmin) < TOL, f"zmin expected ~0, got {bb.zmin}"
        assert abs(bb.xmax - leg_ox) < TOL, f"xmax expected ~{leg_ox}, got {bb.xmax}"
        assert abs(bb.ymax - total_h) < TOL, f"ymax expected ~{total_h}, got {bb.ymax}"
        assert abs(bb.zmax - extrude_depth) < TOL, f"zmax expected ~{extrude_depth}, got {bb.zmax}"
    
        # Z extent (extrusion depth)
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z length expected {extrude_depth}, got {bb.zlen}"
    
        # Height check
        assert abs(bb.ylen - total_h) < TOL, f"Height expected {total_h}, got {bb.ylen}"
    
        # Volume check: should be less than bounding box volume (it's a letter shape)
        bbox_vol = bb.xlen * bb.ylen * bb.zlen
        vol = result.val().Volume()
        assert vol > 0, f"Volume should be positive, got {vol}"
        assert vol < bbox_vol, f"Volume {vol} should be less than bbox volume {bbox_vol}"
        # R shape should have reasonable volume (more than 20% of bbox)
        assert vol > 0.15 * bbox_vol, f"Volume {vol} seems too small vs bbox {bbox_vol}"
    
        # Check it's a single solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Check the extrusion depth via faces at min/max Z
        front_faces = result.faces(">Z")
        back_faces = result.faces("<Z")
        assert front_faces.size() >= 1, "Should have at least one front face"
        assert back_faces.size() >= 1, "Should have at least one back face"
    
        # The shape should contain a point in the stem
        stem_point = cq.Vector(7.5, 50, 10)  # middle of stem
        assert result.val().isInside(stem_point), f"Stem point {stem_point} should be inside R"
    
        # The shape should contain a point in the bowl
        bowl_point = cq.Vector(35, 75, 10)  # right side of bowl
        assert result.val().isInside(bowl_point), f"Bowl point {bowl_point} should be inside R"
    
        # The shape should NOT contain a point in the eye (inner cutout)
        eye_point = cq.Vector(20, 75, 10)  # inside the eye
        assert not result.val().isInside(eye_point), f"Eye point {eye_point} should be outside R (in the hole)"
    
        # The shape should NOT contain a point outside the R (to the right of stem, below bowl)
        outside_point = cq.Vector(40, 20, 10)  # below the leg, to the right
        assert not result.val().isInside(outside_point), f"Outside point {outside_point} should be outside R"
    
        print(f"R shape created successfully!")
        print(f"Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        print(f"Volume: {vol:.1f} mm³")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520638/gpt_generated.stl')
