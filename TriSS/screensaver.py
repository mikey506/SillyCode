import pygame
import random
import math
import string


def create_triangle_grid(rows, cols, screen_width, screen_height):
    """
    Generate a grid of triangles that fill the screen.
    Each cell consists of two triangles forming a diamond.
    """
    triangles = []
    triangle_width = screen_width // cols
    triangle_height = screen_height // rows

    for row in range(rows):
        for col in range(cols):
            # Top triangle
            x1 = col * triangle_width
            y1 = row * triangle_height
            x2 = x1 + triangle_width
            y2 = y1 + triangle_height // 2
            x3 = x1
            y3 = y1 + triangle_height
            triangles.append([(x1, y1), (x2, y2), (x3, y3)])

            # Bottom triangle
            x1 = col * triangle_width + triangle_width
            y1 = row * triangle_height
            x2 = x1 - triangle_width
            y2 = y1 + triangle_height // 2
            x3 = x1
            y3 = y1 + triangle_height
            triangles.append([(x1, y1), (x2, y2), (x3, y3)])
    return triangles


def trinary_color(value, color_offset):
    """
    Generate colors based on trinary value with a dynamic offset.
    -1 -> Random bright color
     0 -> Black
     1 -> Random dark color
    """
    if value == -1:
        return ((color_offset * 3) % 255, (color_offset * 5) % 255, (color_offset * 7) % 255)
    elif value == 0:
        return (0, 0, 0)
    elif value == 1:
        return ((color_offset * 4) % 255, (color_offset * 6) % 255, (color_offset * 8) % 255)


def generate_pattern(rows, cols):
    """
    Generate an initial trinary logic pattern.
    """
    return [[random.choice([-1, 0, 1]) for _ in range(cols)] for _ in range(rows)]


def apply_symmetry(pattern, symmetry_type):
    """
    Apply symmetry to the trinary pattern.
    Supported symmetry types: 'horizontal', 'vertical', 'radial'.
    """
    rows = len(pattern)
    cols = len(pattern[0])
    new_pattern = [row[:] for row in pattern]  # Copy the pattern

    if symmetry_type == "horizontal":
        for y in range(rows // 2):
            new_pattern[rows - y - 1] = pattern[y]  # Mirror rows

    elif symmetry_type == "vertical":
        for y in range(rows):
            for x in range(cols // 2):
                new_pattern[y][cols - x - 1] = pattern[y][x]  # Mirror columns

    elif symmetry_type == "radial":
        for y in range(rows):
            for x in range(cols):
                if (x + y) % 2 == 0:  # Example symmetry: alternate parity
                    new_pattern[rows - y - 1][cols - x - 1] = pattern[y][x]

    return new_pattern


def trinary_logic_update(pattern, perturbation_chance=0.01):
    """
    Update the pattern using trinary logic rules.
    Each cell is updated based on a random neighbor's value.
    Introduces random perturbations for unpredictability.
    """
    rows = len(pattern)
    cols = len(pattern[0])
    new_pattern = [[0] * cols for _ in range(rows)]

    for y in range(rows):
        for x in range(cols):
            neighbors = [
                pattern[(y - 1) % rows][(x - 1) % cols],  # Top-left
                pattern[(y - 1) % rows][x],              # Top
                pattern[(y - 1) % rows][(x + 1) % cols],  # Top-right
                pattern[y][(x - 1) % cols],              # Left
                pattern[y][(x + 1) % cols],              # Right
                pattern[(y + 1) % rows][(x - 1) % cols],  # Bottom-left
                pattern[(y + 1) % rows][x],              # Bottom
                pattern[(y + 1) % rows][(x + 1) % cols]   # Bottom-right
            ]
            new_pattern[y][x] = random.choice(neighbors)

            # Add random perturbation for unpredictability
            if random.random() < perturbation_chance:
                new_pattern[y][x] = random.choice([-1, 0, 1])
    return new_pattern


def draw_triangles(screen, triangles, pattern, rows, cols, color_offset, font, ascii_grid):
    """
    Draw the pattern using a grid of triangles with ASCII characters.
    """
    for i, triangle in enumerate(triangles):
        # Determine the row and column based on the triangle index
        row = (i // (cols * 2)) % rows
        col = (i // 2) % cols

        # Get the value from the pattern and calculate the color
        value = pattern[row][col]
        color = trinary_color(value, color_offset)

        # Draw the triangle
        pygame.draw.polygon(screen, color, triangle)

        # Draw ASCII character at the triangle's center
        if value != 0:
            ascii_char = ascii_grid[row][col]
            text = font.render(ascii_char, True, (255, 255, 255))
            center_x = (triangle[0][0] + triangle[1][0] + triangle[2][0]) // 3
            center_y = (triangle[0][1] + triangle[1][1] + triangle[2][1]) // 3
            screen.blit(text, (center_x - 5, center_y - 5))


def generate_ascii_grid(rows, cols):
    """
    Generate a grid of random ASCII characters.
    """
    ascii_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"
    return [[random.choice(ascii_chars) for _ in range(cols)] for _ in range(rows)]


def main():
    # Initialize Pygame
    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Symmetric Triangle Pixel Screensaver with ASCII")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 12)

    # Settings
    rows, cols = 40, 80  # Adjust density of triangles
    triangles = create_triangle_grid(rows, cols, screen_width, screen_height)
    pattern = generate_pattern(rows, cols)
    ascii_grid = generate_ascii_grid(rows, cols)
    running = True
    color_offset = 0
    symmetry_types = ["horizontal", "vertical", "radial"]

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    running = False  # Exit on any key press

            # Update pattern, apply symmetry, and add unpredictability
            pattern = trinary_logic_update(pattern, perturbation_chance=0.02)
            pattern = apply_symmetry(pattern, random.choice(symmetry_types))
            ascii_grid = generate_ascii_grid(rows, cols)

            # Update color offset for smoother cycling
            color_offset = (color_offset + 1) % 255

            # Draw updated pattern
            screen.fill((0, 0, 0))  # Clear screen
            draw_triangles(screen, triangles, pattern, rows, cols, color_offset, font, ascii_grid)
            pygame.display.flip()

            # Limit to 30 frames per second
            clock.tick(30)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
