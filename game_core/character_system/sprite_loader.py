"""
Sprite loader module - handles loading character sprites and animations
"""
import os
import pygame

def load_character_sprites():
    """Load all character sprites from the character folder"""
    sprites = {
        # Idle animations
        "idle_down": [],
        "idle_up": [],
        "idle_left": [],
        "idle_right": [],

        # Attack animations
        "attack_down": [],
        "attack_up": [],
        "attack_left": [],
        "attack_right": [],

        # Run animations
        "run_down": [],
        "run_up": [],
        "run_left": [],
        "run_right": [],

        # Hit animations (for knockback)
        "hit_down": [],
        "hit_up": [],
        "hit_left": [],
        "hit_right": [],

        # Shield animations
        "shield_down": [],
        "shield_up": [],
        "shield_left": [],
        "shield_right": [],

        # Shielded hit animations
        "shield_hit_down": [],
        "shield_hit_up": [],
        "shield_hit_left": [],
        "shield_hit_right": [],

        # Death animations
        "death_down": [],
        "death_up": [],
        "death_left": [],
        "death_right": []
    }

    # Define animation directories
    animation_dirs = {
        # Idle animations
        "idle_down": "character/char_idle_down",
        "idle_up": "character/char_idle_up",
        "idle_left": "character/char_idle_left",
        "idle_right": "character/char_idle_right",

        # Attack animations
        "attack_down": "character/char_attack_down",
        "attack_up": "character/char_attack_up",
        "attack_left": "character/char_attack_left",
        "attack_right": "character/char_attack_right",

        # Run animations
        "run_down": "character/char_run_down",
        "run_up": "character/char_run_up",
        "run_left": "character/char_run_left",
        "run_right": "character/char_run_right",

        # Hit animations (for knockback)
        "hit_down": "character/char_hit_down_anim",
        "hit_up": "character/char_hit_up_anim",
        "hit_left": "character/char_hit_left_anim",
        "hit_right": "character/char_hit_right_anim",

        # Shield animations
        "shield_down": "character/char_shielded",
        "shield_up": "character/char_shielded",
        "shield_left": "character/char_shielded",
        "shield_right": "character/char_shielded",

        # Shielded hit animations
        "shield_hit_down": "character/char_shielded_hit_down_anim",
        "shield_hit_up": "character/char_shielded_hit_up_anim",
        "shield_hit_left": "character/char_shielded_hit_left_anim",
        "shield_hit_right": "character/char_shielded_hit_right_anim",

        # Death animations
        "death_down": "character/char_death_all_dir_anim",
        "death_up": "character/char_death_all_dir_anim",
        "death_left": "character/char_death_all_dir_anim",
        "death_right": "character/char_death_all_dir_anim"
    }

    # Load all animation frames
    for anim_key, anim_path in animation_dirs.items():
        # Check if the animation directory exists
        if not os.path.exists(anim_path):
            print(f"Warning: Animation directory not found: {anim_path}")
            continue

        # Special handling for static shield sprites (but not shield hit animations)
        if anim_key.startswith("shield_") and not anim_key.startswith("shield_hit_"):
            direction = anim_key.split("_")[1]  # Get direction (up, down, left, right)
            try:
                # Load the specific shield sprite for this direction
                shield_file = f"char_shielded_static_{direction}.png"
                img_path = os.path.join(anim_path, shield_file)

                # Check if the specific file exists
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    sprites[anim_key].append(img)
                else:
                    print(f"Warning: Shield sprite not found: {img_path}")

                    # Try to find any shield sprite as a fallback
                    fallback_found = False
                    for file in os.listdir(anim_path):
                        if file.startswith("char_shielded") and file.endswith(".png"):
                            fallback_img_path = os.path.join(anim_path, file)
                            img = pygame.image.load(fallback_img_path).convert_alpha()
                            sprites[anim_key].append(img)
                            fallback_found = True
                            break

                    if not fallback_found:
                        print(f"No fallback shield sprites found in {anim_path}")
            except Exception as e:
                print(f"Error loading shield sprite {img_path}: {e}")
            continue

        # Regular animation handling for non-shield sprites
        # Find all PNG files in the directory
        frame_files = []
        try:
            for file in os.listdir(anim_path):
                if file.startswith("tile") and file.endswith(".png"):
                    frame_files.append(file)

            # Sort the files to ensure correct order
            frame_files.sort()
        except Exception as e:
            print(f"Error reading directory {anim_path}: {e}")
            continue

        # Load each frame
        for file in frame_files:
            try:
                img_path = os.path.join(anim_path, file)
                img = pygame.image.load(img_path).convert_alpha()
                sprites[anim_key].append(img)
            except Exception as e:
                print(f"Error loading sprite {img_path}: {e}")

    # Make sure we have at least one frame for each animation
    for anim_key in sprites:
        if not sprites[anim_key]:
            print(f"Warning: No frames loaded for animation {anim_key}")
            # Use appropriate fallback based on animation type
            if "shield_hit" in anim_key:
                # For shield hit animations, try to use regular hit animations as fallback
                direction = anim_key.split("_")[2]  # Get direction (up, down, left, right)
                hit_key = f"hit_{direction}"
                if hit_key in sprites and sprites[hit_key]:
                    sprites[anim_key] = sprites[hit_key].copy()
                elif "shield" in sprites and sprites["shield_" + direction]:
                    # If hit animation not available, use shield animation
                    sprites[anim_key] = sprites["shield_" + direction].copy()
                elif sprites["idle_down"]:
                    sprites[anim_key] = sprites["idle_down"].copy()
            elif "attack" in anim_key:
                # Use corresponding idle animation as fallback if available
                direction = anim_key.split("_")[1]  # Get direction (up, down, left, right)
                idle_key = f"idle_{direction}"
                if idle_key in sprites and sprites[idle_key]:
                    sprites[anim_key] = sprites[idle_key].copy()
                elif sprites["idle_down"]:
                    sprites[anim_key] = sprites["idle_down"].copy()
            elif sprites["idle_down"]:
                sprites[anim_key] = sprites["idle_down"].copy()

    return sprites
