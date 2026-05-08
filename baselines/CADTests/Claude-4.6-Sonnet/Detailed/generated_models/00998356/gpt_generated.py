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
        base = 1.19143
        height = 0.85714
        half_base = base / 2.0          # 0.595715
        inner_r = 0.094286              # inner circle radius for corner rounding
        outer_r = 0.214604 / 2.0        # outer rounding radius = 0.107302
        hole_dia = 0.094286             # small hole diameter
        hole_r = hole_dia / 2.0         # 0.047143
        extrude_h = 0.085714
    
        # Triangle vertices (in XY plane, base along X, apex at top)
        # Bottom-left: (-half_base, 0), Bottom-right: (half_base, 0), Apex: (0, height)
        bl = (-half_base, 0.0)
        br = (half_base, 0.0)
        apex = (0.0, height)
    
        # --- Step 1: Compute the triangle side slopes ---
        # Left side: from bl to apex
        # Right side: from br to apex
        # Base: from bl to br (horizontal)
    
        # Left side direction vector (normalized)
        left_dx = apex[0] - bl[0]   # 0.595715
        left_dy = apex[1] - bl[1]   # 0.85714
        left_len = math.sqrt(left_dx**2 + left_dy**2)
        left_nx = left_dy / left_len   # inward normal (pointing right)
        left_ny = -left_dx / left_len
    
        # Right side direction vector (normalized)
        right_dx = apex[0] - br[0]  # -0.595715
        right_dy = apex[1] - br[1]  # 0.85714
        right_len = math.sqrt(right_dx**2 + right_dy**2)
        right_nx = -right_dy / right_len  # inward normal (pointing left)
        right_ny = right_dx / right_len
    
        # --- Step 2: Build the 2D profile using Sketch API ---
        # We'll use the Sketch API to create the triangular profile with rounded bottom corners
        # and a flat top cut.
    
        # The top cut: cut the apex with a horizontal line
        # The apex is at (0, height). We'll cut it at some small distance below.
        # "positioned at a height of approximately 0.85714 units from the base"
        # This means the flat edge IS at height 0.85714 - but that's the apex itself.
        # Interpretation: the flat cut is near the top, creating a small flat edge.
        # Let's cut at y = height - 0.05 (small truncation)
        top_cut_y = height - 0.05  # ~0.80714
    
        # Actually re-reading: "Cut off the top corner... positioned at a height of approximately 0.85714"
        # This likely means the flat edge is at y = 0.85714 which IS the apex height.
        # So the cut is very near the top. Let's use a small truncation.
        # The flat width at y = top_cut_y:
        # Left side: x = bl[0] + (top_cut_y - bl[1]) * (left_dx/left_dy) = -half_base + top_cut_y * (half_base/height)
        # Right side: x = br[0] + (top_cut_y - br[1]) * (right_dx/right_dy) = half_base - top_cut_y * (half_base/height)
    
        # Let's use a more meaningful truncation - cut at y = 0.75 * height
        top_cut_y = 0.75 * height  # 0.642855
    
        # At top_cut_y, the triangle width:
        # x_left = -half_base + top_cut_y * (half_base / height)
        # x_right = half_base - top_cut_y * (half_base / height)
        x_at_cut = half_base * (1.0 - top_cut_y / height)
        # x_left = -x_at_cut, x_right = x_at_cut
    
        # --- Step 3: Build profile with CadQuery Sketch ---
        # Use a polygon approach with rounded bottom corners
    
        # Bottom-left corner rounding center:
        # The corner is at bl. The two edges meeting are: base (going right) and left side (going up-right)
        # Inward normal of base = (0, 1)
        # Inward normal of left side = (left_ny, -left_nx) ... let me recalculate
    
        # For bottom-left corner:
        # Edge 1: base going in +X direction, inward normal = (0, +1)
        # Edge 2: left side going toward apex, inward normal points to the right of the triangle
        # The fillet center is at distance outer_r from both edges
    
        # Angle bisector approach for fillet center at bottom-left:
        # Base edge direction from bl: (1, 0), inward normal: (0, 1)
        # Left edge direction from bl to apex: (left_dx/left_len, left_dy/left_len)
        # Inward normal of left edge (pointing into triangle): (left_dy/left_len, -left_dx/left_len)
        # = (0.85714/left_len, -0.595715/left_len)
    
        # Fillet center = bl + outer_r * (n1 + n2) / |n1 + n2| ... actually it's:
        # center = bl + outer_r * (n1_normalized + n2_normalized) / sin(half_angle) ... 
        # Simpler: center is at distance outer_r from both edges along their inward normals
    
        # For bottom-left:
        n1 = np.array([0.0, 1.0])  # inward normal of base
        n2 = np.array([left_dy/left_len, -left_dx/left_len])  # inward normal of left side
        # Bisector direction
        bisector = n1 + n2
        bisector = bisector / np.linalg.norm(bisector)
        # Half angle
        cos_half = np.dot(n1, bisector)
        # Distance from corner to fillet center along bisector
        d = outer_r / cos_half
        bl_center = np.array(bl) + d * bisector
    
        # For bottom-right corner:
        # Base edge direction from br: (-1, 0), inward normal: (0, 1)
        # Right edge direction from br to apex: (right_dx/right_len, right_dy/right_len)
        # Inward normal of right edge: (-right_dy/right_len, right_dx/right_len)
        n3 = np.array([0.0, 1.0])  # inward normal of base
        n4 = np.array([-right_dy/right_len, right_dx/right_len])  # inward normal of right side
        bisector2 = n3 + n4
        bisector2 = bisector2 / np.linalg.norm(bisector2)
        cos_half2 = np.dot(n3, bisector2)
        d2 = outer_r / cos_half2
        br_center = np.array(br) + d2 * bisector2
    
        # --- Step 4: Build the 2D profile using wire drawing ---
        # Profile points (going counterclockwise):
        # Start from bottom-left fillet, go along base, bottom-right fillet, right side, top cut, left side, back
    
        # Tangent points on base for bottom-left fillet:
        # The fillet touches the base at: bl_center + outer_r * (0, -1) projected onto base
        # Actually tangent point on base = (bl_center[0], 0)
        # Tangent point on left side = bl_center + outer_r * (-n2)... 
    
        # Let me use a simpler approach: build the profile as a polygon and use .fillet() in Sketch
    
        # Truncated triangle vertices:
        # Bottom-left: bl
        # Bottom-right: br  
        # Top-right (at cut): (x_at_cut, top_cut_y)
        # Top-left (at cut): (-x_at_cut, top_cut_y)
    
        # Use Sketch with polygon and fillet at bottom corners
        # Top corners won't be filleted (they're the cut corners)
    
        # Actually, let me use a direct wire approach for more control
    
        # Compute tangent points for bottom-left fillet:
        # On base: (bl_center[0] - outer_r * ... )
        # The tangent point on the base (y=0 line) from bl_center:
        t_bl_base = np.array([bl_center[0], 0.0])
        # The tangent point on the left side from bl_center:
        # Project bl_center onto left side line
        # Left side: parametric: bl + t*(apex-bl), t in [0,1]
        # Normal from bl_center to left side:
        left_dir = np.array([left_dx/left_len, left_dy/left_len])
        t_param = np.dot(np.array(bl_center) - np.array(bl), left_dir)
        t_bl_left = np.array(bl) + t_param * left_dir
    
        # Tangent points for bottom-right fillet:
        t_br_base = np.array([br_center[0], 0.0])
        right_dir = np.array([right_dx/right_len, right_dy/right_len])
        t_param2 = np.dot(np.array(br_center) - np.array(br), right_dir)
        t_br_right = np.array(br) + t_param2 * right_dir
    
        # --- Step 5: Build the profile wire ---
        # Going counterclockwise:
        # 1. From t_bl_base along base to t_br_base (straight line)
        # 2. Arc around br_center from t_br_base to t_br_right
        # 3. From t_br_right along right side to top-right cut point
        # 4. Straight line across top cut
        # 5. From top-left cut point along left side to t_bl_left
        # 6. Arc around bl_center from t_bl_left to t_bl_base
    
        # Top cut points on the sides:
        # On right side at y = top_cut_y:
        # Right side: br + t*(apex-br), y = br[1] + t*(apex[1]-br[1]) = t*height = top_cut_y
        t_right_cut = top_cut_y / height
        top_right_pt = np.array(br) + t_right_cut * np.array([right_dx, right_dy])
        # On left side at y = top_cut_y:
        t_left_cut = top_cut_y / height
        top_left_pt = np.array(bl) + t_left_cut * np.array([left_dx, left_dy])
    
        # Build the wire using CadQuery
        profile = (
            cq.Workplane("XY")
            .moveTo(float(t_bl_base[0]), float(t_bl_base[1]))
            .lineTo(float(t_br_base[0]), float(t_br_base[1]))
            .threePointArc(
                (float(br[0]), float(outer_r * 0.3)),  # midpoint of arc (approximate)
                (float(t_br_right[0]), float(t_br_right[1]))
            )
            .lineTo(float(top_right_pt[0]), float(top_right_pt[1]))
            .lineTo(float(top_left_pt[0]), float(top_left_pt[1]))
            .lineTo(float(t_bl_left[0]), float(t_bl_left[1]))
            .threePointArc(
                (float(bl[0]), float(outer_r * 0.3)),  # midpoint of arc (approximate)
                (float(t_bl_base[0]), float(t_bl_base[1]))
            )
            .close()
        )
    
        # --- Step 6: Extrude the profile ---
        solid = profile.extrude(extrude_h)
    
        # --- Step 7: Add small circular holes near each corner ---
        # Hole positions: near bottom-left, bottom-right, and top (flat edge center)
        # Near bottom corners: offset inward from corners
        hole_offset = inner_r + hole_r + 0.01  # small offset from corner
    
        # Bottom-left hole position: along bisector from bl
        bl_hole_pos = np.array(bl) + (inner_r + hole_r + 0.02) * bisector
        br_hole_pos = np.array(br) + (inner_r + hole_r + 0.02) * bisector2
        # Top hole: center of the flat top edge
        top_hole_pos = np.array([(top_left_pt[0] + top_right_pt[0])/2, 
                                  (top_left_pt[1] + top_right_pt[1])/2])
    
        solid = (
            solid.faces(">Z").workplane()
            .pushPoints([
                (float(bl_hole_pos[0]), float(bl_hole_pos[1])),
                (float(br_hole_pos[0]), float(br_hole_pos[1])),
                (float(top_hole_pos[0]), float(top_hole_pos[1]))
            ])
            .hole(hole_dia)
        )
    
        # --- Step 8: Cut rectangular section from top flat edge ---
        # Rectangular cutout from the top flat edge (center of flat edge)
        rect_w = x_at_cut * 0.6  # width of rectangular cut
        rect_h = 0.05            # depth of rectangular cut into the shape
        rect_d = extrude_h       # full depth
    
        solid = (
            solid.faces(">Y").workplane()
            .center(0, extrude_h/2)
            .rect(rect_w, extrude_h)
            .cutBlind(-rect_h)
        )
    
        # --- Step 9: Cut cylindrical hole near base center ---
        cyl_r = inner_r  # 0.094286
        cyl_pos_y = 0.15  # near base center, slightly above base
    
        solid = (
            solid.faces(">Z").workplane()
            .pushPoints([(0.0, cyl_pos_y)])
            .hole(cyl_r * 2)
        )
    
        # --- Step 10: Rotate and translate ---
        # Rotate 90 degrees about X axis to stand upright, then translate
        result = (
            solid
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((0, 0, extrude_h / 2))
        )
    
        # --- Final object verification ---
        TOL = 0.01
        bb = result.val().BoundingBox()
    
        # After rotation (90° about X): original XY plane becomes XZ plane
        # Original dims: X ~ base (1.19143), Y ~ height (0.85714), Z ~ extrude_h (0.085714)
        # After 90° rotation about X: new X=old X, new Y=-old Z, new Z=old Y
        # So: xlen ~ base, ylen ~ extrude_h, zlen ~ height
    
        print(f"Bounding box: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
        print(f"Volume: {result.val().Volume():.6f}")
        print(f"Faces: {result.faces().size()}")
        print(f"Cylindrical faces: {result.faces('%Cylinder').size()}")
    
        # Check overall bounding box is reasonable
        assert bb.xlen > 0.5, f"X extent too small: {bb.xlen}"
        assert bb.ylen > 0.0, f"Y extent too small: {bb.ylen}"
        assert bb.zlen > 0.0, f"Z extent too small: {bb.zlen}"
    
        # After rotation, the extrude direction (originally Z) maps to Y
        # xlen should be close to base width
        assert abs(bb.xlen - base) < 0.15, f"X (base) expected ~{base}, got {bb.xlen}"
    
        # Volume should be positive and less than bounding box volume
        vol = result.val().Volume()
        bb_vol = bb.xlen * bb.ylen * bb.zlen
        assert vol > 0, f"Volume must be positive, got {vol}"
        assert vol < bb_vol, f"Volume {vol} exceeds bounding box volume {bb_vol}"
    
        # Should have cylindrical faces from holes
        cyl_faces = result.faces('%Cylinder').size()
        assert cyl_faces >= 3, f"Expected at least 3 cylindrical faces (holes), got {cyl_faces}"
    
        # Check the object has reasonable number of faces
        n_faces = result.faces().size()
        assert n_faces >= 8, f"Expected at least 8 faces, got {n_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998356/gpt_generated.stl')
