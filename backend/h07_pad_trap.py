from h07_extra_trap import decide, mask_temp
from h07_surface_trap import looks_empty, paint

def run_decide(temp_c: float):
    return decide(temp_c)

def run_mask(temp_c: float):
    return mask_temp(temp_c)

def run_paint(temp_c: float):
    return paint(temp_c)

def bundle_empty(temp_c: float) -> bool:
    return looks_empty(paint(temp_c))

def pipeline(temp_c: float):
    v, r = run_decide(temp_c)
    return v, r, run_paint(temp_c), run_mask(temp_c)

