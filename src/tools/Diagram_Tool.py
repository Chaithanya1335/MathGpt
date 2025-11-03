from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import base64
import io
import json
import re

class DiagramInput(BaseModel):
    """Schema for diagram generation."""
    diagram_type: str = Field(
        ..., 
        description="Type of diagram: 'vector', 'graph', 'coordinate', 'geometry', 'function', 'custom'"
    )
    description: str = Field(
        ..., 
        description="Detailed description of what the diagram should show, including dimensions, angles, labels, colors, etc."
    )
    title: str = Field(
        default="Diagram",
        description="Title for the diagram"
    )


class GenerateDiagramTool(BaseTool):
    name: str = "Generate Mathematical Diagram"
    description: str = (
        "Generates mathematical diagrams (vectors, graphs, coordinate systems, geometric shapes, etc.) "
        "based on a detailed description. "
        "ONLY use this tool when the question EXPLICITLY asks for visual representation such as: "
        "'represent graphically', 'draw', 'show diagram', 'plot', 'graph', or when dealing with "
        "vectors, geometric shapes, coordinate systems, or function visualization. "
        "DO NOT use for pure algebraic, calculus, or theoretical questions without visual requirements. "
        "The tool creates a PNG image encoded as base64 that can be embedded in the response."
    )
    args_schema: Type[BaseModel] = DiagramInput

    def _run(self, diagram_type: str, description: str, title: str = "Diagram") -> str:
        """Executes the diagram generation logic."""
        try:
            # Parse description for dimensions and parameters
            description_lower = description.lower()
            
            # Create figure (reduced size for better display)
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_aspect('equal')
            
            # Generate based on diagram type
            if diagram_type == "vector" or "vector" in description_lower or "displacement" in description_lower:
                self._draw_vector_diagram(ax, description, title)
            elif diagram_type == "graph" or "function" in description_lower or "plot" in description_lower:
                self._draw_function_graph(ax, description, title)
            elif diagram_type == "coordinate" or "coordinate" in description_lower or "axes" in description_lower:
                self._draw_coordinate_diagram(ax, description, title)
            elif diagram_type == "geometry" or "triangle" in description_lower or "circle" in description_lower or "rectangle" in description_lower:
                self._draw_geometric_diagram(ax, description, title)
            else:
                # Default: try to parse and draw based on description
                self._draw_custom_diagram(ax, description, title)
            
            # Convert to base64 (reduced DPI for smaller file size)
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return json.dumps({
                "diagram_generated": True,
                "diagram_type": diagram_type,
                "title": title,
                "image_base64": img_base64,
                "message": f"Diagram '{title}' has been generated successfully."
            })
            
        except Exception as e:
            return json.dumps({
                "diagram_generated": False,
                "error": str(e),
                "message": f"Error generating diagram: {str(e)}"
            })

    def _draw_vector_diagram(self, ax, description: str, title: str):
        """Draw a vector diagram (like displacement vectors)."""
        # Parse vector parameters from description
        magnitude = self._extract_number(description, ["km", "m", "units"])
        angle_deg = self._extract_number(description, ["°", "degree", "degrees"])
        direction = self._extract_direction(description)
        
        # Default values if not found
        if magnitude is None:
            magnitude = 40
        if angle_deg is None:
            angle_deg = 30
        
        # Convert angle to radians
        if "east of north" in description.lower():
            angle_rad = np.radians(angle_deg)
            # East of north: measured from North axis
            dx = magnitude * np.sin(angle_rad)
            dy = magnitude * np.cos(angle_rad)
        elif "north of east" in description.lower():
            angle_rad = np.radians(angle_deg)
            # North of east: measured from East axis
            dx = magnitude * np.cos(angle_rad)
            dy = magnitude * np.sin(angle_rad)
        else:
            angle_rad = np.radians(angle_deg)
            dx = magnitude * np.cos(angle_rad)
            dy = magnitude * np.sin(angle_rad)
        
        # Draw coordinate system
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        
        # Draw axes labels
        ax.text(0.5, 0.02, 'E', transform=ax.transAxes, ha='center', va='bottom', fontsize=12, weight='bold')
        ax.text(0.02, 0.5, 'N', transform=ax.transAxes, ha='left', va='center', fontsize=12, weight='bold', rotation=90)
        ax.text(0.5, 0.98, 'S', transform=ax.transAxes, ha='center', va='top', fontsize=12, weight='bold')
        ax.text(0.98, 0.5, 'W', transform=ax.transAxes, ha='right', va='center', fontsize=12, weight='bold')
        
        # Draw origin
        ax.plot(0, 0, 'ko', markersize=8)
        ax.text(0, -magnitude*0.1, 'O', ha='center', va='top', fontsize=12, weight='bold')
        
        # Draw vector with tick marks
        # Calculate tick mark positions (divide vector into 4 segments)
        num_segments = 4
        for i in range(1, num_segments):
            tick_x = (dx * i) / num_segments
            tick_y = (dy * i) / num_segments
            # Draw small perpendicular tick marks
            perp_dx = -dy / magnitude * 2  # Perpendicular offset
            perp_dy = dx / magnitude * 2
            ax.plot([tick_x + perp_dx, tick_x - perp_dx], 
                   [tick_y + perp_dy, tick_y - perp_dy], 
                   'k-', linewidth=1)
        
        # Draw the main vector
        arrow = mpatches.FancyArrowPatch(
            (0, 0), (dx, dy),
            arrowstyle='->', mutation_scale=20, linewidth=2.5,
            color='blue', zorder=2
        )
        ax.add_patch(arrow)
        
        # Label the end point
        ax.plot(dx, dy, 'bo', markersize=8)
        ax.text(dx*1.05, dy*1.05, 'P', ha='left', va='bottom', fontsize=12, weight='bold')
        
        # Label the vector (positioned along the vector)
        label_x, label_y = dx*0.55, dy*0.55
        # Offset label slightly perpendicular to vector
        perp_offset_x = -dy / magnitude * 8
        perp_offset_y = dx / magnitude * 8
        ax.text(label_x + perp_offset_x, label_y + perp_offset_y, f'{int(magnitude)}km', 
                ha='center', va='center', fontsize=11, weight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8, edgecolor='black'))
        
        # Draw angle arc
        if "east of north" in description.lower() or angle_deg:
            arc_radius = magnitude * 0.3
            arc = mpatches.Arc((0, 0), arc_radius*2, arc_radius*2, angle=0, 
                             theta1=0, theta2=angle_deg, color='red', linewidth=1.5)
            ax.add_patch(arc)
            ax.text(arc_radius*0.7, arc_radius*0.7, f'{angle_deg}°', 
                   ha='center', va='center', fontsize=10, color='red', weight='bold')
        
        # Draw scale
        scale_length = magnitude / 4
        scale_x = ax.get_xlim()[1] * 0.7
        scale_y = ax.get_ylim()[1] * 0.9
        ax.plot([scale_x, scale_x + scale_length], [scale_y, scale_y], 'k-', linewidth=2)
        ax.text(scale_x + scale_length/2, scale_y + magnitude*0.05, 'Scale', 
               ha='center', va='bottom', fontsize=9, weight='bold')
        ax.text(scale_x + scale_length/2, scale_y - magnitude*0.05, f'{magnitude//4}km', 
               ha='center', va='top', fontsize=9)
        
        # Set limits
        max_dim = max(abs(dx), abs(dy)) * 1.3
        ax.set_xlim(-max_dim*0.2, max_dim)
        ax.set_ylim(-max_dim*0.2, max_dim)
        
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_aspect('equal')

    def _draw_function_graph(self, ax, description: str, title: str):
        """Draw a function graph."""
        x = np.linspace(-10, 10, 1000)
        # Try to extract function expression
        if "sin" in description.lower():
            y = np.sin(x)
        elif "cos" in description.lower():
            y = np.cos(x)
        elif "quadratic" in description.lower() or "x^2" in description.lower():
            y = x**2
        else:
            y = x
        
        ax.plot(x, y, 'b-', linewidth=2)
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=14, weight='bold')

    def _draw_coordinate_diagram(self, ax, description: str, title: str):
        """Draw a coordinate system diagram."""
        ax.axhline(y=0, color='k', linestyle='-', linewidth=1)
        ax.axvline(x=0, color='k', linestyle='-', linewidth=1)
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=14, weight='bold')

    def _draw_geometric_diagram(self, ax, description: str, title: str):
        """Draw geometric shapes."""
        if "triangle" in description.lower():
            triangle = mpatches.Polygon([[0, 0], [4, 0], [2, 3]], closed=True, 
                                       edgecolor='blue', facecolor='lightblue', linewidth=2)
            ax.add_patch(triangle)
        elif "circle" in description.lower():
            radius = self._extract_number(description, ["radius", "r=", "r ="]) or 2
            circle = mpatches.Circle((0, 0), radius, edgecolor='blue', facecolor='lightblue', linewidth=2)
            ax.add_patch(circle)
        
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=14, weight='bold')

    def _draw_custom_diagram(self, ax, description: str, title: str):
        """Draw a custom diagram based on description."""
        # Basic coordinate system
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=14, weight='bold')
        ax.set_aspect('equal')

    def _extract_number(self, text: str, keywords: list = None) -> float:
        """Extract a number from text, optionally following keywords."""
        if keywords is None:
            keywords = []
        text_lower = text.lower()
        # First try with keywords if provided
        for keyword in keywords:
            pattern = rf'{re.escape(keyword.lower())}\s*[=:]*\s*(\d+\.?\d*)'
            match = re.search(pattern, text_lower)
            if match:
                return float(match.group(1))
            # Also try pattern where number comes before keyword
            pattern = rf'(\d+\.?\d*)\s*{re.escape(keyword.lower())}'
            match = re.search(pattern, text_lower)
            if match:
                return float(match.group(1))
        # Try to find any number in the text (prefer larger numbers for vectors/magnitudes)
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            # Return the largest number (likely the magnitude)
            return float(max(numbers, key=lambda x: float(x)))
        return None

    def _extract_direction(self, text: str) -> str:
        """Extract direction information from text."""
        text_lower = text.lower()
        if "east" in text_lower and "north" in text_lower:
            if text_lower.index("east") < text_lower.index("north"):
                return "east of north"
            else:
                return "north of east"
        return None

