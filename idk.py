from manim import *
import numpy as np

class FireworkMechanism(Scene):
    def construct(self):
        # Background aesthetic
        self.camera.background_color = "#0B0C10"

        # ----------------------------------------------------
        # ACT 1: SHELL ANATOMY (CROSS-SECTION)
        # ----------------------------------------------------
        title = Text("How an Aerial Firework Shell Works", font_size=28, weight=BOLD, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        section_sub = Text("Cross-Section View of an Aerial Shell", font_size=18, color=GRAY_B)
        section_sub.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(section_sub))

        # Shell Components
        shell_casing = Circle(radius=1.75, color=GREY_C, stroke_width=5)
        shell_casing.set_fill(DARK_GRAY, opacity=0.3)
        shell_casing.shift(DOWN * 0.3)

        burst_core = Circle(radius=0.75, color=RED_E, fill_color=RED_D, fill_opacity=0.7, stroke_width=3)
        burst_core.move_to(shell_casing.get_center())

        # Star pellets ring
        star_count = 18
        star_radius = 1.25
        star_angles = np.linspace(0, TAU, star_count, endpoint=False)
        colors = [GOLD, YELLOW, RED_A, ORANGE]
        
        stars = VGroup(*[
            Dot(
                point=shell_casing.get_center() + np.array([
                    star_radius * np.cos(a),
                    star_radius * np.sin(a),
                    0
                ]),
                radius=0.12,
                color=colors[i % len(colors)]
            )
            for i, a in enumerate(star_angles)
        ])

        # Internal Time Fuse
        fuse_start = shell_casing.get_bottom() + DOWN * 0.5
        time_fuse = Line(
            start=fuse_start,
            end=burst_core.get_center(),
            color="#FFD166",
            stroke_width=5
        )

        # Lift Charge Pouch (At the bottom of the shell)
        lift_pouch = RoundedRectangle(
            corner_radius=0.2,
            width=1.5,
            height=0.6,
            color=MAROON,
            fill_color=MAROON_E,
            fill_opacity=0.85,
            stroke_width=3
        )
        lift_pouch.next_to(shell_casing, DOWN, buff=0.08)

        # Build Shell visually
        self.play(Create(shell_casing), Create(lift_pouch), run_time=1.2)
        self.play(Create(burst_core), Create(time_fuse), FadeIn(stars), run_time=1.2)
        self.wait(0.5)

        # Labels & Callout Pointers (Strictly separated left & right)
        # Left side callouts
        lbl_lift = Text("1. Lift Charge\n(Propels shell upward)", font_size=15, color=MAROON_B)
        lbl_lift.to_edge(LEFT, buff=0.8).shift(DOWN * 1.5)
        arrow_lift = Arrow(lbl_lift.get_right(), lift_pouch.get_left(), color=MAROON_B, stroke_width=2, buff=0.15)

        lbl_fuse = Text("2. Time-Delay Fuse\n(Controls apex detonation)", font_size=15, color="#FFD166")
        lbl_fuse.to_edge(LEFT, buff=0.8).shift(UP * 0.5)
        arrow_fuse = Arrow(lbl_fuse.get_right(), time_fuse.get_left() + UP * 0.2, color="#FFD166", stroke_width=2, buff=0.15)

        # Right side callouts
        lbl_core = Text("3. Burst Charge\n(Shatters casing at peak)", font_size=15, color=RED_B)
        lbl_core.to_edge(RIGHT, buff=0.8).shift(DOWN * 0.5)
        arrow_core = Arrow(lbl_core.get_left(), burst_core.get_right(), color=RED_B, stroke_width=2, buff=0.15)

        lbl_stars = Text("4. Pyrotechnic Stars\n(Chemical color pellets)", font_size=15, color=GOLD)
        lbl_stars.to_edge(RIGHT, buff=0.8).shift(UP * 1.2)
        arrow_stars = Arrow(lbl_stars.get_left(), stars[2].get_right(), color=GOLD, stroke_width=2, buff=0.15)

        callouts = VGroup(
            lbl_lift, arrow_lift,
            lbl_fuse, arrow_fuse,
            lbl_core, arrow_core,
            lbl_stars, arrow_stars
        )

        self.play(LaggedStartMap(FadeIn, callouts, lag_ratio=0.3), run_time=2.0)
        self.wait(2.0)

        # Cleanly fade out all text and labels to avoid clutter
        self.play(FadeOut(callouts), FadeOut(section_sub))
        
        # ----------------------------------------------------
        # ACT 2: PHASE 1 - THE MORTAR LAUNCH
        # ----------------------------------------------------
        phase1_title = Text("Phase 1: Mortar Tube Ignition", font_size=20, color=YELLOW)
        phase1_title.next_to(title, DOWN, buff=0.25)
        phase1_desc = Text("The bottom lift charge fires inside a steel/HDPE mortar tube.", font_size=16, color=WHITE)
        phase1_desc.next_to(phase1_title, DOWN, buff=0.15)

        self.play(FadeIn(phase1_title), FadeIn(phase1_desc))

        # Group shell and scale down into mortar size
        shell_group = VGroup(shell_casing, burst_core, stars, time_fuse, lift_pouch)
        
        mortar_left = Line(LEFT * 1.1 + DOWN * 3.6, LEFT * 1.1 + DOWN * 0.8, color=GRAY, stroke_width=6)
        mortar_right = Line(RIGHT * 1.1 + DOWN * 3.6, RIGHT * 1.1 + DOWN * 0.8, color=GRAY, stroke_width=6)
        mortar_bottom = Line(LEFT * 1.1 + DOWN * 3.6, RIGHT * 1.1 + DOWN * 3.6, color=GRAY, stroke_width=6)
        mortar_tube = VGroup(mortar_left, mortar_right, mortar_bottom)

        self.play(
            shell_group.animate.scale(0.48).move_to(DOWN * 2.3),
            Create(mortar_tube),
            run_time=1.2
        )
        self.wait(0.5)

        # Ignition flash at the base
        lift_flash = Flash(
            shell_group[-1].get_bottom(),
            color=ORANGE,
            line_length=0.4,
            num_lines=16,
            flash_radius=0.5
        )
        
        gas_pressure_lbl = Text("Rapid gas expansion builds behind shell", font_size=15, color=ORANGE)
        gas_pressure_lbl.next_to(mortar_bottom, UP, buff=0.3)

        self.play(lift_flash, FadeIn(gas_pressure_lbl), run_time=0.4)
        self.wait(0.4)

        # Shell launches upward out of the tube
        self.play(
            shell_group.animate.shift(UP * 7.5),
            FadeOut(gas_pressure_lbl),
            rate_func=rush_into,
            run_time=0.9
        )
        self.play(FadeOut(mortar_tube), FadeOut(phase1_title), FadeOut(phase1_desc))

        # ----------------------------------------------------
        # ACT 3: PHASE 2 - ASCENT & DELAY FUSE
        # ----------------------------------------------------
        phase2_title = Text("Phase 2: Coasting & Internal Time Fuse", font_size=20, color=YELLOW)
        phase2_title.next_to(title, DOWN, buff=0.25)
        phase2_desc = Text("While coasting to peak altitude, the internal fuse burns slowly.", font_size=16, color=WHITE)
        phase2_desc.next_to(phase2_title, DOWN, buff=0.15)
        
        self.play(FadeIn(phase2_title), FadeIn(phase2_desc))

        # Restore shell to center for clear visualization of the burn
        shell_group.scale(1.8).move_to(DOWN * 0.4)
        # Lift pouch is now burnt/empty
        lift_pouch.set_fill(BLACK, opacity=0.8).set_stroke(DARK_GRAY)

        self.play(FadeIn(shell_group), run_time=0.8)

        # Animated burning spark moving through the time-delay fuse
        spark = Dot(point=time_fuse.get_start(), radius=0.1, color=YELLOW)
        spark_halo = Dot(point=time_fuse.get_start(), radius=0.2, color=ORANGE, fill_opacity=0.5)
        burning_fuse = VGroup(spark_halo, spark)

        fuse_note = Text("Delay fuse burns inward (approx. 3-5 seconds)", font_size=15, color="#FFD166")
        fuse_note.next_to(shell_casing, RIGHT, buff=0.8)
        fuse_arrow = Arrow(fuse_note.get_left(), spark.get_right(), color="#FFD166", stroke_width=2)

        self.play(FadeIn(burning_fuse), FadeIn(fuse_note), Create(fuse_arrow))

        # Burn proceeds to center
        self.play(
            burning_fuse.animate.move_to(burst_core.get_center()),
            time_fuse.animate.set_color(DARK_GRAY),
            run_time=2.5,
            rate_func=linear
        )
        self.wait(0.3)

        self.play(
            FadeOut(fuse_note),
            FadeOut(fuse_arrow),
            FadeOut(phase2_title),
            FadeOut(phase2_desc)
        )

        # ----------------------------------------------------
        # ACT 4: PHASE 3 - DETONATION & BURST
        # ----------------------------------------------------
        phase3_title = Text("Phase 3: Burst Charge Detonation at Apex", font_size=20, color=YELLOW)
        phase3_title.next_to(title, DOWN, buff=0.25)
        phase3_desc = Text("Central black powder detonates, igniting stars and propelling them symmetrically.", font_size=16, color=WHITE)
        phase3_desc.next_to(phase3_title, DOWN, buff=0.15)

        self.play(FadeIn(phase3_title), FadeIn(phase3_desc))

        # Flash at center
        core_flash = Flash(
            burst_core.get_center(),
            color=WHITE,
            line_length=0.7,
            num_lines=28,
            flash_radius=1.2
        )
        
        shockwave = Circle(radius=0.1, color=WHITE, stroke_width=5).move_to(burst_core.get_center())

        self.play(
            core_flash,
            shockwave.animate.scale(28).set_opacity(0),
            FadeOut(shell_casing),
            FadeOut(burst_core),
            FadeOut(time_fuse),
            FadeOut(lift_pouch),
            FadeOut(burning_fuse),
            run_time=0.5
        )

        # Radial Star Explosion
        star_burst_anims = []
        burst_distance = 3.2
        for i, star in enumerate(stars):
            angle = star_angles[i]
            target_vector = np.array([
                burst_distance * np.cos(angle),
                burst_distance * np.sin(angle) - 0.4, # slight gravitational drop
                0
            ])
            # Spark trails and dispersion
            star_burst_anims.append(
                star.animate.shift(target_vector).scale(1.4).set_color(
                    interpolate_color(GOLD, RED, (i % 3) / 2)
                )
            )

        self.play(*star_burst_anims, run_time=1.2, rate_func=rush_from)
        
        # Twinkle and fade out
        self.play(
            *[star.animate.scale(0.1).set_opacity(0) for star in stars],
            FadeOut(phase3_title),
            FadeOut(phase3_desc),
            run_time=0.9
        )
        self.wait(0.5)

        # ----------------------------------------------------
        # ACT 5: THE CHEMISTRY OF COLOR
        # ----------------------------------------------------
        chem_title = Text("The Chemistry of Fireworks: What Gives Stars Color?", font_size=22, color=GOLD)
        chem_title.next_to(title, DOWN, buff=0.25)
        chem_desc = Text("Different metal salts produce specific emission wavelengths when heated.", font_size=16, color=WHITE)
        chem_desc.next_to(chem_title, DOWN, buff=0.15)

        self.play(FadeIn(chem_title), FadeIn(chem_desc))

        # Color Elements Table (Clean, aligned structure)
        elements_data = [
            ("Strontium (Sr)", "Crimson Red", "#FF3333"),
            ("Barium (Ba)", "Bright Green", "#33FF57"),
            ("Copper (Cu)", "Electric Blue", "#3388FF"),
            ("Sodium (Na)", "Vibrant Gold/Yellow", "#FFD700"),
            ("Magnesium (Mg)", "Brilliant White Sparks", "#FFFFFF")
        ]

        table_rows = VGroup()
        for elem, color_name, hex_val in elements_data:
            swatch = Dot(radius=0.15, color=hex_val)
            elem_text = Text(elem, font_size=16, weight=BOLD, color=WHITE)
            color_text = Text(color_name, font_size=16, color=hex_val)
            
            row = VGroup(swatch, elem_text, color_text).arrange(RIGHT, buff=0.4)
            table_rows.add(row)

        table_rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        table_rows.move_to(DOWN * 0.8)

        self.play(LaggedStartMap(FadeIn, table_rows, lag_ratio=0.2), run_time=2.0)
        self.wait(2.5)

        # Final Cleanup
        self.play(FadeOut(table_rows), FadeOut(chem_title), FadeOut(chem_desc), FadeOut(title))
        self.wait(0.5)