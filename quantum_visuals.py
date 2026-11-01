from manim import *
import numpy as np

class GeneratedScene(Scene):
    def construct(self):
        # Safe margins
        LEFT_MARGIN = -6.0
        RIGHT_MARGIN = 6.0
        TOP_MARGIN = 3.2
        BOTTOM_MARGIN = -3.2

        # Build a simple feed-forward network: 3 layers (4, 4, 2 nodes)
        layer_sizes = [4, 4, 2]
        layer_gap = 2.5
        node_radius = 0.25
        node_color = BLUE
        edge_color = GREY_B
        edge_stroke = 1.0

        layers = VGroup()
        for i, size in enumerate(layer_sizes):
            layer = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=0.6, stroke_width=1.5) for _ in range(size)])
            layer.arrange(DOWN, buff=0.5)
            layer.shift(RIGHT * i * layer_gap)
            layers.add(layer)

        # Center the whole network vertically
        layers.center()
        # Ensure within horizontal margins
        if layers.get_left()[0] < LEFT_MARGIN:
            layers.shift(RIGHT * (LEFT_MARGIN - layers.get_left()[0]))
        if layers.get_right()[0] > RIGHT_MARGIN:
            layers.shift(LEFT * (layers.get_right()[0] - RIGHT_MARGIN))

        # Edges between layers
        edges = VGroup()
        for i in range(len(layer_sizes) - 1):
            left_layer = layers[i]
            right_layer = layers[i + 1]
            for l_node in left_layer:
                for r_node in right_layer:
                    line = Line(l_node.get_right(), r_node.get_left(), color=edge_color, stroke_width=edge_stroke)
                    edges.add(line)

        network = VGroup(edges, layers)
        # Add layer labels
        layer_labels = VGroup(
            Text("Input", font_size=20).next_to(layers[0], LEFT, buff=0.4),
            Text("Hidden", font_size=20).next_to(layers[1], UP, buff=0.4),
            Text("Output", font_size=20).next_to(layers[2], RIGHT, buff=0.4)
        )

        # Initial animation: show network and mention random weights
        self.play(FadeIn(network, lag_ratio=0.05), FadeIn(layer_labels), run_time=1.5)
        self.wait(1.0)  # "So, how does it learn?"

        # Visualize random weights: flash edges randomly
        import random
        edge_list = list(edges)
        random.shuffle(edge_list)
        flashes = []
        for e in edge_list[:30]:  # subset for speed
            flashes.append(Flash(e.get_center(), color=YELLOW, line_length=0.2, num_lines=4, flash_radius=0.15, run_time=0.3))
        self.play(Succession(*flashes, lag_ratio=0.02), run_time=2.5)  # "At first, the weights are totally random."

        # Pulse traveling left to right
        pulse = Circle(radius=0.15, color=YELLOW, fill_opacity=1, stroke_width=0)
        pulse.move_to(layers[0].get_left() + LEFT * 0.5)
        self.add(pulse)

        # Path: through each layer's center
        path_points = [layers[0].get_center(), layers[1].get_center(), layers[2].get_center()]
        # Move pulse along path
        self.play(
            MoveAlongPath(pulse, VMobject().set_points_smoothly(path_points), rate_func=linear),
            run_time=2.0
        )  # "The network makes a guess"

        # At output layer, show "Guess: Dog"
        guess_text = Text("Guess: Dog", font_size=28, color=GREEN).next_to(layers[2], RIGHT, buff=0.8)
        self.play(FadeIn(guess_text, shift=LEFT * 0.3), run_time=0.5)
        self.wait(1.0)  # "and it's usually wrong."

        # Red X appears over guess
        red_x = MathTex("\\times", color=RED, font_size=48).move_to(guess_text.get_center())
        self.play(FadeIn(red_x, scale=1.5), run_time=0.5)

        # "Correct: Cat" appears next to it
        correct_text = Text("Correct: Cat", font_size=28, color=BLUE).next_to(guess_text, DOWN, buff=0.4)
        self.play(FadeIn(correct_text, shift=UP * 0.2), run_time=0.5)

        # Red line connecting the two texts labeled "Loss/Error"
        line_start = guess_text.get_bottom() + DOWN * 0.1
        line_end = correct_text.get_top() + UP * 0.1
        loss_line = Line(line_start, line_end, color=RED, stroke_width=3)
        loss_label = Text("Loss / Error", font_size=20, color=RED).next_to(loss_line, RIGHT, buff=0.2)
        self.play(Create(loss_line), FadeIn(loss_label), run_time=1.5)

        # Final wait to match total duration
        # Sum of run_times so far: 1.5+1.0+2.5+2.0+0.5+1.0+0.5+0.5+1.5 = 11.0
        # Need 16.136 - 11.0 = 5.136 seconds remaining
        self.wait(5.136)

        # Clean fade out
        self.play(FadeOut(VGroup(network, layer_labels, pulse, guess_text, red_x, correct_text, loss_line, loss_label)), run_time=1.0)