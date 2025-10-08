const examples = {
        "BraceAnnotation": `from manim import *

class BraceAnnotation(Scene):
    def construct(self):
        dot = Dot([-2, -1, 0])
        dot2 = Dot([2, 1, 0])
        line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
        b1 = Brace(line)
        b1text = b1.get_text("Horizontal distance")
        b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
        b2text = b2.get_tex("x-x_1")
        self.add(line, dot, dot2, b1, b2, b1text, b2text)
`,
        "BooleanOperations": `from manim import *

class BooleanOperations(Scene):
    def construct(self):
        # Create two ellipses
        ellipse1 = Ellipse(
            width=4.0,
            height=5.0,
            fill_opacity=0.5,
            color=BLUE,
            stroke_width=10
        ).move_to(LEFT)
        ellipse2 = ellipse1.copy().set_color(color=RED).move_to(RIGHT)

        # Group for initial display
        bool_ops_text = MarkupText("<u>Boolean Operations</u>").next_to(ellipse1, UP * 3)
        ellipse_group = Group(bool_ops_text, ellipse1, ellipse2).move_to(LEFT * 3)
        self.play(FadeIn(ellipse_group))
        self.wait(1)

        # Union
        union_text = Text("Union").next_to(ellipse_group, UP * 3)
        # The Union class performs the union operation on mobjects.
        union_mobject = Union(ellipse1, ellipse2, fill_opacity=0.5, color=GREEN)
        self.play(
            Transform(ellipse_group, Group(union_text, union_mobject.copy().move_to(LEFT * 3))),
            FadeOut(bool_ops_text)
        )
        self.wait(1)

        # Intersection
        intersection_text = Text("Intersection").next_to(ellipse_group, UP * 3)
        # The Intersection class performs the intersection operation.
        intersection_mobject = Intersection(ellipse1, ellipse2, fill_opacity=0.5, color=YELLOW)
        self.play(
            Transform(ellipse_group, Group(intersection_text, intersection_mobject.copy().move_to(LEFT * 3))),
            FadeOut(union_text)
        )
        self.wait(1)

        # Difference (ellipse1 - ellipse2)
        difference_text = Text("Difference (Blue - Red)").next_to(ellipse_group, UP * 3)
        # The Difference class subtracts the second mobject from the first.
        difference_mobject = Difference(ellipse1, ellipse2, fill_opacity=0.5, color=PURPLE)
        self.play(
            Transform(ellipse_group, Group(difference_text, difference_mobject.copy().move_to(LEFT * 3))),
            FadeOut(intersection_text)
        )
        self.wait(1)

        # Exclusion (XOR)
        exclusion_text = Text("Exclusion (XOR)").next_to(ellipse_group, UP * 3)
        # The Exclusion class finds the XOR between two VMobjects.
        exclusion_mobject = Exclusion(ellipse1, ellipse2, fill_opacity=0.5, color=ORANGE)
        self.play(
            Transform(ellipse_group, Group(exclusion_text, exclusion_mobject.copy().move_to(LEFT * 3))),
            FadeOut(difference_text)
        )
        self.wait(2)
`,
        "PointMovingOnShapes": `from manim import *

class PointMovingOnShapes(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        square = Square(side_length=2, color=RED)
        triangle = Triangle(color=GREEN)

        # Create a dot that will move along the shapes
        dot = Dot(color=YELLOW)

        # Add shapes to the scene
        self.add(circle, square, triangle)

        # Animate the dot moving along the circle
        self.play(MoveAlongPath(dot, circle), run_time=2)
        self.wait(0.5)

        # Animate the dot moving along the square
        self.play(MoveAlongPath(dot, square), run_time=2)
        self.wait(0.5)

        # Animate the dot moving along the triangle
        self.play(MoveAlongPath(dot, triangle), run_time=2)
        self.wait(0.5)

        # You can also chain paths or create more complex movements
        # For example, moving from the triangle back to the circle
        self.play(MoveAlongPath(dot, Line(triangle.get_center(), circle.get_center())), run_time=1)
        self.play(MoveAlongPath(dot, circle), run_time=2)
        self.wait(1)
`,
        "MovingAngle": `from manim import *

class MovingAngleExample(Scene):
    def construct(self):
        rotation_center = LEFT
        theta_tracker = ValueTracker(110)

        line1 = Line(ORIGIN, RIGHT * 4).shift(rotation_center)
        line2 = Line(ORIGIN, RIGHT * 4).shift(rotation_center)
        line2.rotate(theta_tracker.get_value() * DEGREES, about_point=rotation_center)

        arc = Angle(line1, line2, radius=0.8, other_angle=False)
        
        # Create a label for the angle
        label = MathTex(r"\\theta").next_to(arc, UP)

        self.add(line1, line2, arc, label)

        self.play(
            theta_tracker.animate.set_value(40),
            run_time=2
        )
        self.wait(0.5)

        self.play(
            theta_tracker.animate.set_value(200),
            run_time=3
        )
        self.wait(0.5)

        # Update the angle and label dynamically
        arc.add_updater(
            lambda m: m.become(Angle(line1, line2, radius=0.8, other_angle=False))
        )
        label.add_updater(
            lambda m: m.next_to(arc, UP)
        )
        line2.add_updater(
            lambda m: m.set_rotation(theta_tracker.get_value() * DEGREES, about_point=rotation_center)
        )

        self.play(
            theta_tracker.animate.set_value(110),
            run_time=2
        )
        self.wait(1)
`,
        "SinAndCosFunctionPlot": `from manim import *

class SinAndCosFunctionPlot(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-2 * PI, 2 * PI, PI / 2],  # X-axis from -2π to 2π with π/2 steps
            y_range=[-1.5, 1.5, 0.5],           # Y-axis from -1.5 to 1.5 with 0.5 steps
            x_length=10,                        # Length of the X-axis
            y_length=6,                         # Length of the Y-axis
            axis_config={"color": GRAY},
            tips=False,
        ).add_coordinates()

        # Create labels for the axes
        labels = axes.get_axis_labels(
            x_label=Tex("x"),
            y_label=Tex("f(x)")
        )

        # Define the sine and cosine functions
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)

        # Create labels for the functions
        sin_label = axes.get_graph_label(sin_graph, Tex("sin(x)"), x_val=PI/2, direction=UP)
        cos_label = axes.get_graph_label(cos_graph, Tex("cos(x)"), x_val=0, direction=UP)

        # Add everything to the scene
        self.play(Create(axes), Write(labels))
        self.play(Create(sin_graph), Create(cos_graph))
        self.play(Write(sin_label), Write(cos_label))
        self.wait(2)
`
    };