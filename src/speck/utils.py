"""Helper functions with cross-application uses"""

def _hex_to_rgb(hex: str, alpha: float = 1) -> tuple[int, int, int]:
        "Convert hex string to RGB"
        hex = hex.lstrip('#')
        color = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        alpha_int = alpha*255
        return (*color, alpha_int)