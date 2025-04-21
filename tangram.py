import re
import math


class TangramPuzzle:
    def __init__(self, filename):
        self.filename = filename
        self.transformations = {}
        self.pieces = []
        self._parse_tex()
        self._compute_vertices()

    def _parse_tex(self):
        piece_labels = [
            "Large triangle 1",
            "Large triangle 2",
            "Medium triangle",
            "Small triangle 1",
            "Small triangle 2",
            "Square",
            "Parallelogram"
        ]

        pattern = re.compile(r"\\PieceTangram\\[TangSol](?:<(.*?)>)?\\((.*?),(.*?)\\)\\{(.*?)\\}")

        with open(self.filename, 'r') as file:
            content = file.read()

        # Extract only lines with \PieceTangram
        lines = [line for line in content.splitlines() if "\\PieceTangram" in line and not line.strip().startswith("%")]

        piece_index = 0
        for line in lines:
            match = re.search(r"\\PieceTangram\[TangSol\](?:<([^>]*)>)?\(([^,]+),([^)]+)\)\{([^}]+)\}",
                              line.replace(" ", ""))
            if not match:
                continue

            options_str, x_coord, y_coord, piece_type = match.groups()

            xflip = yflip = False
            rotate = 0

            if options_str:
                options = [opt.strip() for opt in options_str.split(',')]
                for opt in options:
                    if opt == 'xscale=-1':
                        xflip = True
                    elif opt == 'yscale=-1':
                        yflip = True
                    elif opt.startswith('rotate='):
                        rotate = int(opt.split('=')[1]) % 360

            self.transformations[piece_labels[piece_index]] = {
                'xflip': xflip,
                'yflip': yflip,
                'rotate': rotate
            }
            self.pieces.append({
                'name': piece_labels[piece_index],
                'x': int(x_coord),
                'y': int(y_coord),
                'transform': self.transformations[piece_labels[piece_index]]
            })

            piece_index += 1
        # print(piece_index)

        assert piece_index == 7, f"Expected 7 pieces, found {piece_index}"

    def _rotate(self, x, y, degrees):
        """
        function to rotate the diagram
        :param x: x coordinate
        :param y: y coordinate
        :param degrees: degrees for rotation. 90 degrees, 180 degrees etc
        :return: updated x & y coordinates
        """
        radians = math.radians(degrees)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return (
            round(x * cos_a - y * sin_a, 5),
            round(x * sin_a + y * cos_a, 5)
        )

    def _compute_vertices(self):
        """
        Function to compute the vertices
        """
        shape_templates = {
            "Large triangle 1": [(0, 0), (1, 0), (0, 1)],
            "Large triangle 2": [(0, 0), (1, 0), (0, 1)],
            "Medium triangle": [(0, 0), (1, 0), (0, 1)],
            "Small triangle 1": [(0, 0), (1, 0), (0, 1)],
            "Small triangle 2": [(0, 0), (1, 0), (0, 1)],
            "Square": [(0, 0), (1, 0), (1, 1), (0, 1)],
            "Parallelogram": [(0, 0), (1, 0), (1.5, 1), (0.5, 1)]
        }

        for piece in self.pieces:
            name = piece['name']
            x_anchor = piece['x']
            y_anchor = piece['y']
            transform = piece['transform']
            base_vertices = shape_templates[name]

            transformed = []
            for x, y in base_vertices:
                # 1. Rotate
                x_rot, y_rot = self._rotate(x, y, transform['rotate'])
                # 2. Flip
                if transform['xflip']:
                    x_rot *= -1
                if transform['yflip']:
                    y_rot *= -1
                # 3. Translate
                x_final = round(x_rot + x_anchor, 5)
                y_final = round(y_rot + y_anchor, 5)
                transformed.append((x_final, y_final))

            # Sort clockwise starting from leftmost topmost point
            min_point = min(transformed, key=lambda p: (p[0], -p[1]))
            min_idx = transformed.index(min_point)
            piece['vertices'] = transformed[min_idx:] + transformed[:min_idx]

    def draw_pieces(self, filename):
        """
        function to store puzzle output in a tex file.
        :param filename:
        :return:
        """
        all_x = [x for piece in self.pieces for x, _ in piece['vertices']]
        all_y = [y for piece in self.pieces for _, y in piece['vertices']]
        min_x, max_x = min(all_x) - 2, max(all_x) + 2
        min_y, max_y = min(all_y) - 2, max(all_y) + 2

        with open(filename, 'w') as f:
            f.write("\\documentclass{article}\n")
            f.write("\\usepackage{tikz}\n")
            f.write("\\usepackage[margin=0.5in]{geometry}\n")
            f.write("\\begin{document}\n")
            f.write("\\begin{tikzpicture}[scale=1]\n")

            # Draw grid
            f.write(f"  \\draw[step=5mm,gray,very thin] ({min_x},{min_y}) grid ({max_x},{max_y});\n")

            # Draw origin marker
            f.write("  \\filldraw[red] (0,0) circle (1pt);\n")

            for piece in self.pieces:
                vertices = piece['vertices']
                coords = ' -- '.join([f"({x},{y})" for x, y in vertices] + [f"({vertices[0][0]},{vertices[0][1]})"])
                f.write(f"  \\draw[thick, fill=blue!20] {coords};\n")

            f.write("\\end{tikzpicture}\n")
            f.write("\\end{document}\n")

    def __str__(self):
        output = []
        for piece in self.pieces:
            output.append(f"{piece['name']}:")
            for v in piece['vertices']:
                output.append(f"  ({v[0]}, {v[1]})")
        return "\n".join(output)



puzzle = TangramPuzzle("kangaroo.tex")
# print(puzzle.transformations)

print(puzzle)
x, y = puzzle._rotate(1, 0, 90)

puzzle.draw_pieces("pieces_output.tex")
