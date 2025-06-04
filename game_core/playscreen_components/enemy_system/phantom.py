"""
Phantom Enemy - A ghost-like enemy that uses pathfinding to navigate toward the player
"""
import pygame
import os
import heapq
import math
from .enemy import Enemy
from game_core.other_components.debug_tools import debug_manager

class Phantom(Enemy):
    """Phantom enemy class with cardinal movement"""
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="phantom")

        # Load phantom animations
        self.load_animation("idle", "left", "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_left")
        self.load_animation("idle", "right", "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_right")
        self.load_animation("run", "left", "Enemies_Sprites/Phantom_Sprites/phantom_run_anim_left")
        self.load_animation("run", "right", "Enemies_Sprites/Phantom_Sprites/phantom_run_anim_right")

        # Load hit animations
        self.load_animation("hit", "left", "Enemies_Sprites/Phantom_Sprites/phantom_hit_anim_left")
        self.load_animation("hit", "right", "Enemies_Sprites/Phantom_Sprites/phantom_hit_anim_right")

        # Load death animations
        self.load_animation("death", "left", "Enemies_Sprites/Phantom_Sprites/phantom_death_anim_left")
        self.load_animation("death", "right", "Enemies_Sprites/Phantom_Sprites/phantom_death_anim_right")

        # Set initial image and rect based on direction
        initial_anim_key = f"idle_{self.direction}"
        if initial_anim_key in self.sprites and self.sprites[initial_anim_key]:
            self.image = self.sprites[initial_anim_key][0]
        elif "idle_right" in self.sprites and self.sprites["idle_right"]:
            self.image = self.sprites["idle_right"][0]

        # Create the rect but don't set position yet - EnemyManager will handle that
        self.rect = self.image.get_rect()
        # Just store the initial position - actual positioning will be done by EnemyManager
        self.rect.topleft = (x, y)

        # Phantom-specific properties
        self.speed = 0.5  # Movement speed (reduced from 1.0)

        # Store position as floats for precise movement
        self.float_x = 0.0
        self.float_y = 0.0

        # Detection range (15 tiles)
        self.detection_range = 15 * 16  # 15 tiles * 16 pixels per tile = 240 pixels
        self.show_detection_range = False  # Don't show the detection circle

        # Movement cooldown to prevent jittery movement
        self.move_cooldown = 0
        self.move_cooldown_time = 5  # Reduced from 10 to make movement more responsive

        # Direction persistence to reduce zig-zagging
        self.last_direction = None  # Track the last movement direction
        self.direction_persistence = 15  # Frames to maintain the same direction

        # Debug flag
        self.debug_mode = False  # Disable debug output

        # Knockback properties
        self.knockback_strength = 5.0  # Increased strength of knockback when hitting player
        self.knockback_cooldown = 0  # Cooldown to prevent continuous knockback
        self.knockback_cooldown_time = 45  # Frames to wait between knockbacks (about 0.75 seconds)

        # Health and damage properties
        self.max_health = 100  # Increased from 30 to 100
        self.current_health = 100  # Increased from 30 to 100
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 20  # Frames to show hit animation
        self.hit_frame = 0
        self.hit_animation_speed = 0.15

        # Damage cooldown to prevent multiple hits from a single attack
        self.damage_cooldown = 0
        self.damage_cooldown_time = 30  # Frames to wait between taking damage (0.5 seconds)

        # Death properties
        self.is_dying = False
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 60  # Frames to show death animation
        self.death_frame = 0
        self.death_animation_speed = 0.1  # Slower animation for death

        # Health bar properties
        self.show_health_bar = False
        self.health_bar_timer = 0
        self.health_bar_duration = 120  # Show health bar for 2 seconds (60 frames per second)

        # Pathfinding properties
        self.path = []  # List of grid positions to follow
        self.path_update_timer = 0
        self.path_update_interval = 30  # Update path every 30 frames (0.5 seconds)
        self.max_path_length = 20  # Maximum number of steps to calculate
        self.current_path_index = 0
        self.grid_size = 16  # Size of each grid cell

        # Load health bar assets
        self.health_bar_bg = self.load_image("Enemies_Sprites/Hud_Ui/health_hud.png")      # Background (doesn't change size)
        self.health_indicator = self.load_image("Enemies_Sprites/Hud_Ui/health_bar_hud.png")  # Indicator (changes size with health)

        # Scale health bar to be smaller for enemies
        scale_factor = 0.5
        if self.health_bar_bg and self.health_indicator:
            # Scale the background (health_bar_hud.png)
            self.health_bar_bg = pygame.transform.scale(
                self.health_bar_bg,
                (int(self.health_bar_bg.get_width() * scale_factor),
                 int(self.health_bar_bg.get_height() * scale_factor))
            )

            # Scale the indicator (health_hud.png) to be slightly smaller than the background
            # Make it 90% of the background width to ensure it fits inside
            indicator_scale = scale_factor * 0.9
            self.health_indicator = pygame.transform.scale(
                self.health_indicator,
                (int(self.health_indicator.get_width() * indicator_scale),
                 int(self.health_indicator.get_height() * indicator_scale))
            )



    def check_collision(self, collision_handler, tile_mapping, map_data):
        """Check if the phantom would collide with any solid tile corners"""
        # If no collision data is available, assume no collision
        if not collision_handler or not tile_mapping or not map_data:
            return False

        # Create a rect for the phantom's next position
        next_rect = pygame.Rect(
            int(self.float_x + self.velocity[0]),
            int(self.float_y + self.velocity[1]),
            self.rect.width,
            self.rect.height
        )

        # Use the collision handler to check for collisions
        return collision_handler.check_collision(next_rect, tile_mapping, map_data)



    def move_towards_player(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Move the phantom towards the player with collision avoidance"""
        # Decrement cooldown
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # Calculate if we've reached the player's rectangle
        player_rect = pygame.Rect(player_x - 8, player_y - 8, 16, 16)
        if self.rect.colliderect(player_rect):
            # We've reached the player, stop moving
            self.velocity = [0, 0]
            self.state = "idle"
            return

        # Calculate direct direction to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery

        # Calculate distance to player
        distance_to_player = math.sqrt(dx**2 + dy**2)

        # Define a proximity threshold where we'll use smoother movement
        proximity_threshold = 160  # About 10 tiles - increased for smoother movement

        if distance_to_player <= proximity_threshold:
            # When close to the player, use smoother diagonal movement
            # Normalize the direction vector
            if distance_to_player > 0:  # Avoid division by zero
                dx = dx / distance_to_player
                dy = dy / distance_to_player

            # Set velocity - move directly toward player but at the correct speed
            self.velocity[0] = dx * self.speed
            self.velocity[1] = dy * self.speed

            # Set direction based on horizontal movement for animation
            if dx != 0:
                self.direction = "right" if dx > 0 else "left"
        else:
            # When farther away, use cardinal directions with persistence
            # to reduce zig-zagging

            # Normalize the direction vector
            if distance_to_player > 0:  # Avoid division by zero
                norm_dx = dx / distance_to_player
                norm_dy = dy / distance_to_player
            else:
                norm_dx, norm_dy = 0, 0

            # Determine if we should move horizontally or vertically
            move_horizontal = abs(norm_dx) > abs(norm_dy)

            # Check if we should maintain the previous direction for persistence
            if self.last_direction == "horizontal" and self.direction_persistence > 0:
                move_horizontal = True
                self.direction_persistence -= 1
            elif self.last_direction == "vertical" and self.direction_persistence > 0:
                move_horizontal = False
                self.direction_persistence -= 1
            else:
                # Set new direction and reset persistence
                self.last_direction = "horizontal" if move_horizontal else "vertical"
                self.direction_persistence = 10  # Reduced for more responsive movement

            if move_horizontal:
                # Move horizontally
                self.velocity[0] = self.speed if norm_dx > 0 else -self.speed
                self.velocity[1] = 0
                self.direction = "right" if norm_dx > 0 else "left"
            else:
                # Move vertically
                self.velocity[0] = 0
                self.velocity[1] = self.speed if norm_dy > 0 else -self.speed
                # Keep the left/right direction for animation purposes
                if norm_dx != 0:
                    self.direction = "right" if norm_dx > 0 else "left"

        # Check for collisions with the new velocity
        if collision_handler and tile_mapping and map_data:
            # If we would collide, stop moving
            if self.check_collision(collision_handler, tile_mapping, map_data):
                # Try to find an alternative direction
                # Try the four cardinal directions
                for test_dir in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    # Set test velocity
                    test_velocity = [test_dir[0] * self.speed, test_dir[1] * self.speed]

                    # Save original velocity
                    original_velocity = self.velocity.copy()

                    # Set velocity to test velocity
                    self.velocity = test_velocity

                    # Check if this would cause a collision
                    if not self.check_collision(collision_handler, tile_mapping, map_data):
                        # This direction is clear, keep it
                        if test_dir[0] != 0:
                            self.direction = "right" if test_dir[0] > 0 else "left"
                        break

                    # Restore original velocity if this direction also collides
                    self.velocity = original_velocity

                # If all directions cause collisions, stop moving
                if self.check_collision(collision_handler, tile_mapping, map_data):
                    self.velocity = [0, 0]

        # Set animation state based on movement
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.state = "run"
        else:
            self.state = "idle"

        # Set cooldown to prevent jittery movement
        # Use a shorter cooldown when close to the player for smoother movement
        if distance_to_player <= proximity_threshold:
            self.move_cooldown = 0  # No cooldown when close for smooth movement
        else:
            self.move_cooldown = self.move_cooldown_time

        # Debug output
        if hasattr(self, 'debug_mode') and self.debug_mode:
            debug_manager.log(f"Phantom moving: velocity={self.velocity}, state={self.state}, direction={self.direction}, distance={distance_to_player:.1f}", "enemy")

    def apply_knockback_to_player(self, player, **_):
        """Apply knockback to the player when colliding

        Note: Additional parameters are accepted for compatibility with the enemy manager
        but are no longer used since the player handles collision detection internally.
        We use **_ to indicate that we're intentionally ignoring these parameters."""
        # Skip if on cooldown, hit, dying or dead
        if self.knockback_cooldown > 0 or self.is_hit or self.is_dying or self.is_dead:
            return False

        # Check if we're colliding with the player
        if self.rect.colliderect(player.rect):
            # Calculate knockback direction (away from phantom)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            # Always apply knockback effect to player with the calculated direction
            # The player's apply_knockback method will handle shield hit animation without knockback when shielded
            if hasattr(player, 'apply_knockback'):
                player.apply_knockback(dx, dy)

            # Apply damage to the player if the method exists and not shielded
            if hasattr(player, 'take_damage'):
                player.take_damage(10)  # Phantom deals 10 damage

            # Start cooldown
            self.knockback_cooldown = self.knockback_cooldown_time

            # Debug output
            if self.debug_mode:
                from game_core.other_components.debug_tools import debug_manager
                debug_manager.log(f"Applied knockback to player: dx={dx:.2f}, dy={dy:.2f}", "enemy")

            return True
        return False

    def load_image(self, path):
        """Load an image from the specified path"""
        full_path = os.path.join(os.getcwd(), path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            return image
        except pygame.error as e:
            pass  # Error loading image
            # Return a placeholder image (red square)
            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
            placeholder.fill((255, 0, 0, 128))
            return placeholder

    def take_damage(self, damage_amount=10, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply damage to the phantom and trigger hit animation

        Args:
            damage_amount (int): Amount of damage to apply
            knockback_x (float): X component of knockback direction
            knockback_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Only take damage if not already dying or dead and not on cooldown
        if self.is_dying or self.is_dead or self.damage_cooldown > 0:
            return False

        # Reduce health
        self.current_health -= damage_amount

        # Show health bar
        self.show_health_bar = True
        self.health_bar_timer = self.health_bar_duration

        # Start damage cooldown to prevent multiple hits from a single attack
        self.damage_cooldown = self.damage_cooldown_time

        # Check if phantom should die
        if self.current_health <= 0:
            self.current_health = 0
            self.start_death_animation()
            return True

        # Apply knockback if direction is provided
        if knockback_x != 0 or knockback_y != 0:
            # Normalize the knockback direction to ensure consistent knockback distance
            distance = ((knockback_x ** 2) + (knockback_y ** 2)) ** 0.5
            if distance > 0:
                # Scale knockback by a factor to ensure it's strong enough to move the enemy
                # but not so strong that it goes through walls
                knockback_factor = min(distance, 10) / distance  # Cap the knockback distance
                normalized_x = (knockback_x / distance) * knockback_factor * self.knockback_strength
                normalized_y = (knockback_y / distance) * knockback_factor * self.knockback_strength

                # Use the base class knockback method with normalized direction
                super().apply_knockback(normalized_x, normalized_y, collision_handler, tile_mapping, map_data)
            else:
                # Fallback if direction is invalid
                super().apply_knockback(knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

        # Start hit animation
        self.start_hit_animation()
        return True

    def start_hit_animation(self):
        """Start the hit animation sequence"""
        self.is_hit = True
        self.hit_timer = self.hit_duration
        self.hit_frame = 0
        self.animation_timer = 0
        self.state = "hit"

    def start_death_animation(self):
        """Start the death animation sequence"""
        self.is_dying = True
        self.is_hit = False  # Cancel any hit animation
        self.death_timer = self.death_duration
        self.death_frame = 0
        self.animation_timer = 0
        self.state = "death"
        self.velocity = [0, 0]  # Stop movement

    def draw(self, surface, camera_x=0, camera_y=0, zoom_factor=1.0):
        """Draw the enemy on the given surface, accounting for camera position and zoom"""
        # Draw detection range circle if enabled
        if self.show_detection_range:
            # Calculate screen position for circle center
            # Keep logical coordinates, only scale for visual representation
            logical_center_x = self.rect.centerx - camera_x
            logical_center_y = self.rect.centery - camera_y

            # Scale the screen position for zoom
            screen_center_x = logical_center_x * zoom_factor
            screen_center_y = logical_center_y * zoom_factor

            # Scale the detection range with zoom factor
            scaled_detection_range = int(self.detection_range * zoom_factor)

            # Draw a red circle with the detection range
            pygame.draw.circle(
                surface,
                (255, 0, 0),  # Red color
                (screen_center_x, screen_center_y),
                scaled_detection_range,  # Scaled radius
                max(1, int(1 * zoom_factor))  # Scale line width, minimum 1
            )

        # Call the parent class draw method to draw the enemy sprite
        super().draw(surface, camera_x, camera_y, zoom_factor)

        # Draw health bar if needed
        if self.show_health_bar and not self.is_dead and self.health_bar_bg and self.health_indicator:
            # Calculate the entity's screen position accounting for zoom
            entity_screen_x = (self.rect.centerx - camera_x) * zoom_factor
            entity_screen_y = (self.rect.y - camera_y) * zoom_factor

            # Calculate health bar position relative to the scaled entity position
            health_bar_width = self.health_bar_bg.get_width()
            health_bar_height = self.health_bar_bg.get_height()
            screen_x = entity_screen_x - (health_bar_width // 2)
            screen_y = entity_screen_y - health_bar_height - (5 * zoom_factor)  # 5 pixels above enemy, scaled

            # Calculate health percentage
            health_percent = max(0, min(1, self.current_health / self.max_health))

            # Calculate width of health_hud (background) based on current health
            health_width = int(health_bar_width * health_percent)

            if health_width > 0:
                # Create a subsurface of the health_hud (background) with the appropriate width
                try:
                    # Create a subsurface of the background (health_hud) with the appropriate width
                    health_rect = pygame.Rect(0, 0, health_width, health_bar_height)
                    health_bg_part = self.health_bar_bg.subsurface(health_rect)

                    # Draw the health_hud (background) first
                    surface.blit(health_bg_part, (screen_x, screen_y))

                    # Draw the health_bar_hud (foreground) on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))
                except ValueError:
                    # If subsurface fails, use clipping rect
                    clip_rect = surface.get_clip()

                    health_clip_rect = pygame.Rect(
                        screen_x,
                        screen_y,
                        health_width,
                        health_bar_height
                    )

                    # Draw the health_hud (background) with clipping
                    surface.set_clip(health_clip_rect)
                    surface.blit(self.health_bar_bg, (screen_x, screen_y))
                    surface.set_clip(clip_rect)

                    # Draw the health_bar_hud (foreground) on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))

    def update_animation(self):
        """Update the phantom's animation frame"""
        # Handle death animation
        if self.is_dying:
            # Determine the animation key
            current_animation_key = f"death_{self.direction}"

            # Check if the animation exists
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                # Try the other direction if this one doesn't exist
                other_direction = "left" if self.direction == "right" else "right"
                current_animation_key = f"death_{other_direction}"

                # If still no animation, fall back to idle
                if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                    current_animation_key = f"idle_{self.direction}"

            # Update death animation timer
            self.animation_timer += self.death_animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.death_frame += 1

                # Check if death animation is complete
                if self.death_frame >= len(self.sprites[current_animation_key]):
                    # Mark as dead but keep the last frame
                    self.is_dead = True
                    self.death_frame = len(self.sprites[current_animation_key]) - 1

            # Use death frame for rendering
            frame_index = min(self.death_frame, len(self.sprites[current_animation_key]) - 1)
            self.image = self.sprites[current_animation_key][frame_index]

        # Handle hit animation
        elif self.is_hit:
            # Determine the animation key
            current_animation_key = f"hit_{self.direction}"

            # Check if the animation exists
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                # Try the other direction if this one doesn't exist
                other_direction = "left" if self.direction == "right" else "right"
                current_animation_key = f"hit_{other_direction}"

                # If still no animation, fall back to idle
                if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                    current_animation_key = f"idle_{self.direction}"

            # Update hit animation timer
            self.animation_timer += self.hit_animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.hit_frame += 1

                # Check if hit animation is complete
                if self.hit_frame >= len(self.sprites[current_animation_key]):
                    # Reset hit state
                    self.is_hit = False
                    self.hit_frame = 0
                    self.state = "idle"

            # Use hit frame for rendering
            frame_index = min(self.hit_frame, len(self.sprites[current_animation_key]) - 1)
            self.image = self.sprites[current_animation_key][frame_index]

        # Regular animation handling
        else:
            # Use the base class animation update for normal states
            super().update_animation()

    def find_path_to_player(self, player_x, player_y, collision_handler, tile_mapping, map_data):
        """Find a path to the player using A* algorithm"""
        # Convert positions to grid coordinates
        start_x = self.rect.centerx // self.grid_size
        start_y = self.rect.centery // self.grid_size
        goal_x = player_x // self.grid_size
        goal_y = player_y // self.grid_size

        # Don't pathfind if player is too far away
        distance = math.sqrt((goal_x - start_x)**2 + (goal_y - start_y)**2)
        distance_pixels = distance * self.grid_size
        if distance_pixels > self.detection_range:  # Only pathfind within detection range
            self.path = []
            return

        # A* algorithm
        open_set = []
        closed_set = set()
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self.heuristic(start_x, start_y, goal_x, goal_y)}

        # Add start node to open set
        heapq.heappush(open_set, (f_score[(start_x, start_y)], (start_x, start_y)))

        while open_set and len(closed_set) < 100:  # Limit search to prevent infinite loops
            # Get node with lowest f_score
            current = heapq.heappop(open_set)[1]

            # Check if we reached the goal
            if current == (goal_x, goal_y):
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                # Reverse path (from start to goal)
                path.reverse()

                # Limit path length
                if len(path) > self.max_path_length:
                    path = path[:self.max_path_length]

                self.path = path
                return

            # Add current to closed set
            closed_set.add(current)

            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Four cardinal directions
                neighbor_x = current[0] + dx
                neighbor_y = current[1] + dy
                neighbor = (neighbor_x, neighbor_y)

                # Skip if out of bounds
                if (neighbor_y < 0 or neighbor_x < 0 or
                    neighbor_y >= len(map_data) or neighbor_x >= len(map_data[0])):
                    continue

                # Skip if already evaluated
                if neighbor in closed_set:
                    continue

                # Check if this neighbor is walkable (no collision)
                test_rect = pygame.Rect(
                    neighbor_x * self.grid_size + self.grid_size // 4,
                    neighbor_y * self.grid_size + self.grid_size // 4,
                    self.grid_size // 2,
                    self.grid_size // 2
                )

                if collision_handler.check_collision(test_rect, tile_mapping, map_data):
                    # Collision detected, not walkable
                    continue

                # Calculate tentative g_score
                tentative_g_score = g_score.get(current, float('inf')) + 1

                # Skip if this path is worse
                if neighbor in g_score and tentative_g_score >= g_score[neighbor]:
                    continue

                # This path is better, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + self.heuristic(neighbor_x, neighbor_y, goal_x, goal_y)

                # Add to open set if not already there
                if not any(neighbor == node[1] for node in open_set):
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # If we get here, no path was found
        self.path = []

    def heuristic(self, x1, y1, x2, y2):
        """Manhattan distance heuristic for A* algorithm"""
        return abs(x1 - x2) + abs(y1 - y2)

    def follow_path(self, collision_handler, tile_mapping, map_data):
        """Follow the calculated path"""
        if not self.path or self.current_path_index >= len(self.path):
            return

        # Get current target position
        target_x, target_y = self.path[self.current_path_index]
        target_pixel_x = target_x * self.grid_size + self.grid_size // 2
        target_pixel_y = target_y * self.grid_size + self.grid_size // 2

        # Calculate direction to target
        dx = target_pixel_x - self.rect.centerx
        dy = target_pixel_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Check if we've reached the current target
        if distance < self.speed * 1.5:
            self.current_path_index += 1
            return

        # Move towards target
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance

            # Set velocity
            self.velocity[0] = dx * self.speed
            self.velocity[1] = dy * self.speed

            # Set direction for animation
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"

            # Set animation state
            self.state = "run"
        else:
            self.velocity = [0, 0]
            self.state = "idle"

        # Store original position for collision detection
        original_x = self.rect.x
        original_y = self.rect.y

        # Apply movement
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Check for collisions
        if collision_handler and tile_mapping and map_data:
            if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                # Collision detected, revert to original position
                self.rect.x = original_x
                self.rect.y = original_y

                # Try to find a new path
                self.path = []
                self.path_update_timer = self.path_update_interval

        # Update animation
        self.update_animation()

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update phantom position and animation"""
        # Skip updates if dead
        if self.is_dead:
            return

        # Update timers
        if self.knockback_cooldown > 0:
            self.knockback_cooldown -= 1

        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0 and self.is_hit:
                self.is_hit = False

        if self.death_timer > 0:
            self.death_timer -= 1

        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= 1
            if self.health_bar_timer <= 0:
                self.show_health_bar = False

        # Initialize float position if not already set
        if self.float_x == 0.0 and self.float_y == 0.0:
            self.float_x = float(self.rect.x)
            self.float_y = float(self.rect.y)

        # Check if being knocked back (using base class property)
        if hasattr(self, 'is_knocked_back') and self.is_knocked_back:
            # Let the base class handle knockback movement
            super().update(player_x, player_y)

            # Update float position from rect position after knockback
            self.float_x = float(self.rect.x)
            self.float_y = float(self.rect.y)

            # Check for collisions after knockback
            if collision_handler and tile_mapping and map_data:
                # If we collided with a wall during knockback, stop the knockback and move back to a valid position
                if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                    # Store original position
                    original_x = self.rect.x
                    original_y = self.rect.y

                    # Try moving back in the opposite direction of knockback
                    # First try X direction
                    if self.knockback_velocity[0] != 0:
                        # Move back in the opposite direction of X knockback
                        self.rect.x -= int(self.knockback_velocity[0] * 2)

                        # Check if we're still colliding
                        if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                            # Restore original X position
                            self.rect.x = original_x

                            # Try moving back in the opposite direction of Y knockback
                            if self.knockback_velocity[1] != 0:
                                self.rect.y -= int(self.knockback_velocity[1] * 2)

                                # If still colliding, restore original position
                                if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                                    self.rect.y = original_y

                    # If we didn't try X direction or it didn't work, try Y direction
                    elif self.knockback_velocity[1] != 0:
                        # Move back in the opposite direction of Y knockback
                        self.rect.y -= int(self.knockback_velocity[1] * 2)

                        # Check if we're still colliding
                        if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                            # Restore original Y position
                            self.rect.y = original_y

                    # Update float position from rect position
                    self.float_x = float(self.rect.x)
                    self.float_y = float(self.rect.y)

                    # Stop knockback
                    self.knockback_velocity = [0, 0]
                    self.is_knocked_back = False

        # Only move normally if not hit, dying, or knocked back
        elif not self.is_hit and not self.is_dying:
            # Calculate distance to player
            dx = player_x - self.rect.centerx
            dy = player_y - self.rect.centery
            distance_to_player = math.sqrt(dx**2 + dy**2)

            # Only move if player is within detection range
            if distance_to_player <= self.detection_range:
                # Update pathfinding
                if collision_handler and tile_mapping and map_data:
                    # Update path periodically
                    self.path_update_timer += 1
                    if self.path_update_timer >= self.path_update_interval or not self.path:
                        self.path_update_timer = 0
                        self.find_path_to_player(player_x, player_y, collision_handler, tile_mapping, map_data)
                        self.current_path_index = 0

                    # Follow the path if we have one
                    if self.path and self.current_path_index < len(self.path):
                        # Follow the path
                        self.follow_path(collision_handler, tile_mapping, map_data)

                        # Update float position based on velocity
                        self.float_x += self.velocity[0]
                        self.float_y += self.velocity[1]

                        # Update rect position from float position
                        self.rect.x = int(self.float_x)
                        self.rect.y = int(self.float_y)
                    else:
                        # If no path, use default movement
                        self.move_towards_player(player_x, player_y, collision_handler, tile_mapping, map_data)

                        # Update float position based on velocity
                        self.float_x += self.velocity[0]
                        self.float_y += self.velocity[1]

                        # Update rect position from float position
                        self.rect.x = int(self.float_x)
                        self.rect.y = int(self.float_y)
                else:
                    # If no collision data, use default movement
                    self.move_towards_player(player_x, player_y, collision_handler, tile_mapping, map_data)

                    # Update float position based on velocity
                    self.float_x += self.velocity[0]
                    self.float_y += self.velocity[1]

                    # Update rect position from float position
                    self.rect.x = int(self.float_x)
                    self.rect.y = int(self.float_y)
            else:
                # Player is out of range, stop moving
                self.velocity = [0, 0]
                self.state = "idle"

            # Debug output for actual movement
            if hasattr(self, 'debug_mode') and self.debug_mode:
                debug_manager.log(f"Actual movement: x={self.rect.x}, y={self.rect.y}, float_x={self.float_x:.2f}, float_y={self.float_y:.2f}", "enemy")

        # Update animation
        self.update_animation()
