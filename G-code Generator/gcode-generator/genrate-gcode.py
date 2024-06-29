import cmath
import math
from svgpathtools import svg2paths, Line, Arc, CubicBezier, QuadraticBezier, Path

def circle_to_gcode(circle, scale_factor, num_segments=100):
    """
    Convert a circle to G-code commands by approximating it with arcs.

    Parameters:
    - circle (Path): The circle path to convert.
    - scale_factor (float): Scaling factor for the circle.
    - num_segments (int): Number of line segments to approximate the circle.

    Returns:
    - gcode (str): G-code commands representing the circle.
    - total_distance (float): Total travel distance of the circle.
    """
    center = circle.start * scale_factor
    radius = abs(circle.length()) * scale_factor / (2 * math.pi)

    gcode = ""
    total_distance = 0.0

    for i in range(num_segments + 1):  # Add 1 to ensure the path closes
        theta = 2 * math.pi * (i / num_segments)
        point = center + radius * cmath.rect(1, theta)
        distance = abs(point - center)
        total_distance += distance
        gcode += f"G1 X{point.real:.3f} Y{point.imag:.3f} Z0 ; Travel distance: {distance:.3f}\n"

    return gcode, total_distance

def ellipse_to_gcode(ellipse, scale_factor, num_segments=100):
    """
    Convert an ellipse to G-code commands by approximating it with arcs.

    Parameters:
    - ellipse (Path): The ellipse path to convert.
    - scale_factor (float): Scaling factor for the ellipse.
    - num_segments (int): Number of line segments to approximate the ellipse.

    Returns:
    - gcode (str): G-code commands representing the ellipse.
    - total_distance (float): Total travel distance of the ellipse.
    """
    # Extract ellipse parameters
    center = ellipse.start * scale_factor
    rx = abs(ellipse.rx * scale_factor)
    ry = abs(ellipse.ry * scale_factor)

    gcode = ""
    total_distance = 0.0

    # Approximate ellipse using circular arcs
    for i in range(num_segments + 1):  # Add 1 to ensure the path closes
        theta = 2 * math.pi * (i / num_segments)
        point = center + rx * cmath.rect(1, theta)
        distance = abs(point - center)
        total_distance += distance
        gcode += f"G1 X{point.real:.3f} Y{point.imag:.3f} Z0 ; Travel distance: {distance:.3f}\n"

    return gcode, total_distance

def arc_to_gcode(arc, scale_factor, num_segments=100):
    """
    Convert an arc to G-code commands by approximating it with line segments.

    Parameters:
    - arc (Arc): The arc to convert.
    - scale_factor (float): Scaling factor for the arc.
    - num_segments (int): Number of line segments to approximate the arc.

    Returns:
    - gcode (str): G-code commands representing the arc.
    - total_distance (float): Total travel distance of the arc.
    """
    start = arc.start * scale_factor
    end = arc.end * scale_factor
    center = arc.center * scale_factor
    radius = abs(arc.radius * scale_factor)

    # Determine the direction of the arc
    angle_start = cmath.phase(start - center)
    angle_end = cmath.phase(end - center)
    angle_diff = angle_end - angle_start
    direction = 'CW' if angle_diff < 0 else 'CCW'

    # Convert negative angles to positive
    if direction == 'CW':
        angle_start += 2 * math.pi
        angle_end += 2 * math.pi

    # Calculate the angular step
    theta_diff = angle_end - angle_start
    if direction == 'CW':
        theta_diff = -theta_diff

    gcode = ""
    total_distance = 0.0

    for i in range(num_segments):
        theta1 = angle_start + i * theta_diff / num_segments
        theta2 = angle_start + (i + 1) * theta_diff / num_segments
        point1 = center + radius * cmath.rect(1, theta1)
        point2 = center + radius * cmath.rect(1, theta2)
        distance = abs(point2 - point1)
        total_distance += distance
        gcode += f"G1 X{point2.real:.3f} Y{point2.imag:.3f} Z0 ; Travel distance: {distance:.3f}\n"

    return gcode, total_distance

def svg_to_gcode(svg_file, gcode_file, feedrate=100, scale_factor=1, offset=(0, 0)):
    """
    Convert SVG paths to G-code commands.

    Parameters:
    - svg_file (str): Path to the input SVG file.
    - gcode_file (str): Path to the output G-code file.
    - feedrate (float): Feedrate for the G-code commands (default is 100).
    - scale_factor (float): Scaling factor for the SVG paths (default is 1).
    - offset (tuple): Offset to apply to each coordinate (default is (0, 0)).

    Returns:
    None
    """
    # Parse SVG paths
    paths, _ = svg2paths(svg_file)
    
    # Open G-code file
    with open(gcode_file, 'w') as f:
        # Set units to millimeters and feedrate
        f.write("G21 ; Set units to millimeters\n")
        f.write(f"G1 F{feedrate} ; Set feedrate\n")
        
        # Process each path
        for path in paths:
            for segment in path:
                if segment.length() == 0:
                    continue
                # Convert SVG path segments to G-code commands
                if isinstance(segment, Line):
                    start = segment.start * scale_factor + complex(*offset)
                    end = segment.end * scale_factor + complex(*offset)
                    f.write(f"G1 X{start.real:.3f} Y{start.imag:.3f} Z0\n")
                    f.write(f"G1 X{end.real:.3f} Y{end.imag:.3f} Z0\n")
                elif isinstance(segment, Arc):
                    gcode, distance = arc_to_gcode(segment, scale_factor)
                    f.write(gcode)
                elif isinstance(segment, QuadraticBezier):
                    # Handle QuadraticBezier segments if needed
                    pass
                elif isinstance(segment, Path) and segment.isclosed():
                    # Check if the path is a circle or an ellipse
                    if abs(segment.rx - segment.ry) < 1e-6:  # Check if the path is a circle
                        gcode, distance = circle_to_gcode(segment, scale_factor)
                        f.write(gcode)
                    else:  # Handle ellipses
                        gcode, distance = ellipse_to_gcode(segment, scale_factor)
                        f.write(gcode)

# Example usage
svg_file = "input.svg"
gcode_file = "output.gcode"
feedrate = 100  # Adjust as needed
scale_factor = 1  # Adjust as needed
offset = (10, 10)  # Adjust as needed

svg_to_gcode(svg_file, gcode_file, feedrate, scale_factor, offset)
