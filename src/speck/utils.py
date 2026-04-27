"""Helper functions with cross-application uses"""

def _hex_to_rgb(hex: str, alpha: float = 1, return_as_floats: bool = False) -> tuple[int, int, int, int]:
    "Convert hex string to RGB"
    hex = hex.lstrip('#')
    color = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    alpha_int = int(alpha*255)
    full_tuple = (*color, alpha_int)

    if return_as_floats:
            full_tuple = tuple([v/255 for v in full_tuple]) 

    return full_tuple