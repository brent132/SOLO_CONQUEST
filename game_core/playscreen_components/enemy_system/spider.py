"""
Spider Enemy - A spider enemy that uses A* pathfinding to navigate toward the player
"""
import pygame
import os
import heapq
import math
from .enemy import Enemy

class Spider(Enemy):
    """Spider enemy class - a spider that uses A* pathfinding to navigate toward the player"""
    def __init__(self, x, y):
        """Initialize the Spider enemy"""
        super().__init__(x, y, enemy_type="spider")

        # Set initial direction and state
        self.direction = "right"
        self.state = "idle"

        # Load animations
        self._load_animations()

        # Create the rect but don't set position yet - EnemyManager will handle that
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Health and damage properties
        self._init_health_properties()

        # Load health bar assets
        self._init_health_bar()

        # Movement and pathfinding properties
        self._init_movement_properties()

        # Line of sight and pathfinding properties
        self._init_pathfinding_properties()

        # Set initial state and image
        self.state = "idle"  # Explicitly set to idle state
        self.velocity = [0, 0]  # Ensure velocity is zero

        # Set initial image from idle animation
        initial_anim_key = f"idle_{self.direction}"
        if initial_anim_key in self.sprites and self.sprites[initial_anim_key]:
            self.image = self.sprites[initial_anim_key][0]
            self.frame = 0  # Reset animation frame
        elif "idle_right" in self.sprites and self.sprites["idle_right"]:
            self.image = self.sprites["idle_right"][0]
            self.frame = 0  # Reset animation frame

        # Set initial animation
        self.update_animation()

    def _load_animations(self):
        """Load animation sprites for the spider"""
        # Load spider idle, hit, and death animations for all directions
        for direction in ["right", "left", "up", "down"]:
            self.load_animation("idle", direction, "Enemies_Sprites/Spider_Sprites/spider_idle_anim_all_dir")
            self.load_animation("hit", direction, "Enemies_Sprites/Spider_Sprites/spider_hit_anim_all_dir")
            self.load_animation("death", direction, "Enemies_Sprites/Spider_Sprites/spider_death_anim_all_dir")
            self.load_animation("run", direction, "Enemies_Sprites/Spider_Sprites/spider_run_anim_all_dir")

    def _init_movement_properties(self):
        """Initialize movement-related properties"""
        # Movement properties
        self.speed = 0.5  # Movement speed (reduced from 1.0)
        self.float_x = float(self.rect.x)  # Floating-point position for smoother movement
        self.float_y = float(self.rect.y)

        # Initialize velocity
        self.velocity = [0, 0]

        # Knockback properties
        self.knockback_strength = 4.0  # Strength of knockback when hit by player
        self.knockback_cooldown = 0
        self.knockback_cooldown_time = 45  # Frames to wait between knockbacks (about 0.75 seconds)

        # Player damage properties
        self.player_knockback_strength = 4.0
        self.player_damage = 10

        # Movement cooldown to prevent jittery movement
        self.move_cooldown = 0
        self.move_cooldown_time = 5  # Frames to wait between movement updates

    def _init_pathfinding_properties(self):
        """Initialize pathfinding and line of sight properties"""
        # Line of sight properties
        self.has_seen_player = False  # Flag to track if we've seen the player
        self.sight_range = 200  # Maximum distance to detect player

        # Direction persistence to reduce zig-zagging
        self.last_direction = None  # Track the last movement direction
        self.direction_persistence = 15  # Frames to maintain the same direction

        # A* Pathfinding properties
        self.path = []  # List of grid positions to follow
        self.path_update_timer = 0
        self.path_update_interval = 30  # Update path every 30 frames (0.5 seconds)
        self.max_path_length = 20  # Maximum number of steps to calculate
        self.current_path_index = 0
        self.grid_size = 16  # Size of each grid cell for pathfinding
        self.detection_range = 240  # 15 tiles (16 pixels per tile)

    def _init_health_properties(self):
        """Initialize health-related properties"""
        # Health properties
        self.max_health = 100
        self.current_health = self.max_health
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 20  # Frames to show hit effect
        self.is_dying = False
        self.is_dead = False
        self.death_timer = 0
        self.death_duration = 60  # Frames to show death animation
        self.death_frame = 0
        self.damage_cooldown = 0
        self.damage_cooldown_time = 30  # Frames between taking damage

        # Health bar properties
        self.show_health_bar = False
        self.health_bar_timer = 0
        self.health_bar_duration = 120  # Show health bar for 2 seconds

    def _init_health_bar(self):
        """Initialize health bar assets"""
        # Load health bar assets
        self.health_bar_bg = self.load_image("Enemies_Sprites/Hud_Ui/health_hud.png")
        self.health_indicator = self.load_image("Enemies_Sprites/Hud_Ui/health_bar_hud.png")

        # Scale health bar to be smaller for enemies
        scale_factor = 0.5
        if self.health_bar_bg and self.health_indicator:
            # Scale the background
            self.health_bar_bg = pygame.transform.scale(
                self.health_bar_bg,
                (int(self.health_bar_bg.get_width() * scale_factor),
                 int(self.health_bar_bg.get_height() * scale_factor))
            )

            # Scale the indicator to be slightly smaller than the background
            indicator_scale = scale_factor * 0.9
            self.health_indicator = pygame.transform.scale(
                self.health_indicator,
                (int(self.health_indicator.get_width() * indicator_scale),
                 int(self.health_indicator.get_height() * indicator_scale))
            )

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

    def check_collision(self, collision_handler, tile_mapping, map_data):
        """Check if the spider would collide with any solid tile corners

        Args:
            collision_handler: Collision handler for collision detection
            tile_mapping: Tile mapping for collision detection
            map_data: Map data for collision detection

        Returns:
            bool: True if collision would occur, False otherwise
        """
        # If no collision data is available, assume no collision
        if not collision_handler or not tile_mapping or not map_data:
            return False

        # Create a rect for the spider's next position
        next_rect = pygame.Rect(
            int(self.float_x + self.velocity[0]),
            int(self.float_y + self.velocity[1]),
            self.rect.width,
            self.rect.height
        )

        # Use the collision handler to check for collisions
        return collision_handler.check_collision(next_rect, tile_mapping, map_data)

    def check_line_of_sight(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Check if there's a clear line of sight to the player

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection

        Returns:
            bool: True if there is a clear line of sight, False otherwise
        """
        # Calculate distance to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5

        # If player is too far away, no line of sight
        if distance > self.sight_range:
            return False

        # If no collision handler or map data, assume line of sight
        if not collision_handler or not tile_mapping or not map_data:
            return True

        # Calculate start point for the line of sight check
        start_x, start_y = self.rect.centerx, self.rect.centery
        # Note: player_x and player_y are used directly in the calculations

        # If the distance is very small, we have line of sight
        if distance < 16:  # Less than one tile
            return True

        # Normalize the direction vector
        if distance > 0:
            dx = dx / distance
            dy = dy / distance

        # Check points along the line at regular intervals
        step_size = 8  # Check every 8 pixels
        steps = int(distance / step_size)

        for i in range(1, steps):  # Skip the first step (enemy position)
            # Calculate the point to check
            check_x = start_x + dx * i * step_size
            check_y = start_y + dy * i * step_size

            # Convert to grid coordinates
            grid_x = int(check_x // collision_handler.grid_cell_size)
            grid_y = int(check_y // collision_handler.grid_cell_size)

            # Skip out of bounds tiles
            if grid_y < 0 or grid_x < 0 or grid_y >= len(map_data) or grid_x >= len(map_data[0]):
                continue

            # Get tile ID at this position
            tile_id = map_data[grid_y][grid_x]

            # Skip empty tiles
            if tile_id == -1:
                continue

            # Get tile path from mapping
            tile_path = collision_handler._get_tile_path_from_id(tile_id, tile_mapping)
            if not tile_path:
                continue

            # Check if this tile has collision data
            if tile_path in collision_handler.collision_data:
                # If any corner is active, consider line of sight blocked
                for corner_idx, corner_state in collision_handler.collision_data[tile_path].items():
                    if corner_state:
                        return False

        # If we've checked all points and found no obstacles, we have line of sight
        return True

    def find_path_to_player(self, player_x, player_y, collision_handler, tile_mapping, map_data):
        """Find a path to the player using A* algorithm

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Collision handler for collision detection
            tile_mapping: Tile mapping for collision detection
            map_data: Map data for collision detection
        """
        # Convert positions to grid coordinates
        start_x = self.rect.centerx // self.grid_size
        start_y = self.rect.centery // self.grid_size
        goal_x = player_x // self.grid_size
        goal_y = player_y // self.grid_size

        # Don't pathfind if player is too far away
        distance = math.sqrt((goal_x - start_x)**2 + (goal_y - start_y)**2)
        distance_pixels = distance * self.grid_size
        if distance_pixels > self.detection_range:  # Only pathfind within detection range (15 tiles)
            self.path = []
            self.velocity = [0, 0]  # Stop movement
            self.state = "idle"     # Set to idle state
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
        """Manhattan distance heuristic for A* algorithm

        Args:
            x1 (int): Start x coordinate
            y1 (int): Start y coordinate
            x2 (int): Goal x coordinate
            y2 (int): Goal y coordinate

        Returns:
            float: Heuristic distance between points
        """
        return abs(x1 - x2) + abs(y1 - y2)

    def follow_path(self, collision_handler, tile_mapping, map_data):
        """Follow the calculated path

        Args:
            collision_handler: Collision handler for collision detection
            tile_mapping: Tile mapping for collision detection
            map_data: Map data for collision detection
        """
        if not self.path or self.current_path_index >= len(self.path):
            # No path to follow, set to idle
            self.velocity = [0, 0]
            self.state = "idle"
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
            # If we've reached the end of the path, set to idle
            if self.current_path_index >= len(self.path):
                self.velocity = [0, 0]
                self.state = "idle"
            return

        # Normalize direction
        if distance > 0:
            dx = dx / distance
            dy = dy / distance

        # Set velocity
        self.velocity[0] = dx * self.speed
        self.velocity[1] = dy * self.speed

        # Set direction based on movement for animation
        if abs(dx) > abs(dy):
            # Horizontal movement is dominant
            self.direction = "right" if dx > 0 else "left"
        else:
            # Vertical movement is dominant
            self.direction = "down" if dy > 0 else "up"

        # Only set to run state if actually moving
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.state = "run"
        else:
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

                # Stop movement and set to idle
                self.velocity = [0, 0]
                self.state = "idle"

                # Try to find a new path
                self.path = []
                self.path_update_timer = self.path_update_interval

    def find_path_direction(self, target_x, target_y, collision_handler, tile_mapping, map_data):
        """Find the best direction to move towards the target while avoiding obstacles
        (Legacy method kept for compatibility)

        Args:
            target_x (int): Target x position
            target_y (int): Target y position
            collision_handler: Collision handler for collision detection
            tile_mapping: Tile mapping for collision detection
            map_data: Map data for collision detection

        Returns:
            tuple: (dx, dy) direction vector to move in
        """
        # If no collision data is available, just move directly
        if not collision_handler or not tile_mapping or not map_data:
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            return dx, dy

        # Calculate direct direction to target
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        # Calculate distance to target
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5

        # If we're very close, just return the direct direction
        if distance < 32:  # Less than 2 tiles
            return dx, dy

        # Normalize the direction vector
        if distance > 0:
            norm_dx = dx / distance
            norm_dy = dy / distance
        else:
            return 0, 0  # No movement if we're at the target

        # Check if direct path is clear
        # Create a test velocity in the direct direction
        test_velocity = [norm_dx * self.speed, norm_dy * self.speed]

        # Save original velocity
        original_velocity = self.velocity.copy()

        # Set velocity to test velocity
        self.velocity = test_velocity

        # Check if this would cause a collision
        direct_collision = self.check_collision(collision_handler, tile_mapping, map_data)

        # Restore original velocity
        self.velocity = original_velocity

        # If direct path is clear, use it
        if not direct_collision:
            return dx, dy

        # Try 8 directions around the enemy to find a clear path
        directions = [
            (1, 0),    # Right
            (1, 1),    # Down-right
            (0, 1),    # Down
            (-1, 1),   # Down-left
            (-1, 0),   # Left
            (-1, -1),  # Up-left
            (0, -1),   # Up
            (1, -1)    # Up-right
        ]

        # Sort directions by how close they are to the target direction
        def direction_score(direction):
            # Calculate dot product with normalized target direction
            # Higher dot product means more aligned with target direction
            dot_product = direction[0] * norm_dx + direction[1] * norm_dy
            return -dot_product  # Negative because we want highest dot product first

        directions.sort(key=direction_score)

        # Try each direction until we find one that doesn't cause a collision
        for direction in directions:
            # Create a test velocity in this direction
            test_velocity = [direction[0] * self.speed, direction[1] * self.speed]

            # Set velocity to test velocity
            self.velocity = test_velocity

            # Check if this would cause a collision
            collision = self.check_collision(collision_handler, tile_mapping, map_data)

            # Restore original velocity
            self.velocity = original_velocity

            # If this direction is clear, use it
            if not collision:
                # Scale the direction by the distance to the target
                # This makes the enemy move faster when further from the target
                return direction[0] * min(distance, 50), direction[1] * min(distance, 50)

        # If all directions cause collisions, just return the original direction
        # The collision handling in _move_towards_player will handle this case
        return dx, dy

    def _move_towards_player(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Move the spider towards the player with collision avoidance and line of sight

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
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

        # Calculate distance to player
        dx = player_x - self.rect.centerx
        dy = player_y - self.rect.centery
        distance_to_player = math.sqrt(dx**2 + dy**2)

        # Only move if player is within detection range
        if distance_to_player > self.detection_range:
            # Player too far away, stop moving and set to idle
            self.velocity = [0, 0]
            self.state = "idle"
            self.path = []  # Clear any existing path
            return

        # Check if we have line of sight to the player
        has_line_of_sight = self.check_line_of_sight(player_x, player_y, collision_handler, tile_mapping, map_data)

        # If we have line of sight, update the seen player flag
        if has_line_of_sight:
            # Set the flag that we've seen the player at least once
            self.has_seen_player = True

            # Reset move cooldown to make the enemy move immediately when it sees the player
            self.move_cooldown = 0
        else:
            # No line of sight, stop moving
            self.velocity = [0, 0]
            self.state = "idle"
            return

        # Use pathfinding to find the best direction to move
        dx, dy = self.find_path_direction(player_x, player_y, collision_handler, tile_mapping, map_data)

        # Calculate distance to player
        distance_to_player = ((dx ** 2) + (dy ** 2)) ** 0.5

        # Define a proximity threshold where we'll use smoother movement
        proximity_threshold = 160  # About 10 tiles - for smoother movement

        if distance_to_player <= proximity_threshold:
            # When close to the player, use smoother diagonal movement
            # Normalize the direction vector
            if distance_to_player > 0:  # Avoid division by zero
                dx = dx / distance_to_player
                dy = dy / distance_to_player

            # Set velocity - move directly toward player but at the correct speed
            self.velocity[0] = dx * self.speed
            self.velocity[1] = dy * self.speed

            # Set direction based on movement for animation
            # Spider has 4 directions (up, down, left, right)
            if abs(dx) > abs(dy):
                # Horizontal movement is dominant
                self.direction = "right" if dx > 0 else "left"
            else:
                # Vertical movement is dominant
                self.direction = "down" if dy > 0 else "up"
        else:
            # When farther away, use the pathfinding direction but maintain some persistence
            # to reduce zig-zagging

            # Normalize the direction vector
            if distance_to_player > 0:  # Avoid division by zero
                norm_dx = dx / distance_to_player
                norm_dy = dy / distance_to_player
            else:
                norm_dx, norm_dy = 0, 0

            # Determine if we should move horizontally or vertically based on the pathfinding result
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
                self.direction_persistence = 10  # Reduced from 15 for more responsive pathfinding

            if move_horizontal:
                # Move horizontally in the direction suggested by pathfinding
                self.velocity[0] = self.speed if norm_dx > 0 else -self.speed
                self.velocity[1] = 0
                self.direction = "right" if norm_dx > 0 else "left"
            else:
                # Move vertically in the direction suggested by pathfinding
                self.velocity[0] = 0
                self.velocity[1] = self.speed if norm_dy > 0 else -self.speed
                # Set up/down direction for animation
                self.direction = "down" if norm_dy > 0 else "up"

        # Check for collisions with the new velocity
        if collision_handler and tile_mapping and map_data:
            # If we would collide, stop moving
            if self.check_collision(collision_handler, tile_mapping, map_data):
                # Our pathfinding should have found a clear path, but if we still collide,
                # just stop moving for this frame
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

    def _update_knockback(self, collision_handler=None, tile_mapping=None, map_data=None):
        """Update knockback movement and check for collisions

        Args:
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Update knockback timer
        self.knockback_timer -= 1
        if self.knockback_timer <= 0:
            # Reset knockback state
            self.is_knocked_back = False
            self.knockback_velocity = [0, 0]
            self.state = "idle"
            return

        # Store original position for collision detection
        original_x = self.rect.x
        original_y = self.rect.y

        # Apply knockback movement to float position
        self.float_x += self.knockback_velocity[0]
        self.float_y += self.knockback_velocity[1]

        # Update rect position from float position
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

        # Check for collisions after knockback if collision data is available
        if collision_handler and tile_mapping and map_data:
            if collision_handler.check_collision(self.rect, tile_mapping, map_data):
                # We'll handle this in the main update method for more sophisticated collision response
                # Just revert position for now
                self.rect.x = original_x
                self.rect.y = original_y
                self.float_x = float(original_x)
                self.float_y = float(original_y)
                return

        # Gradually reduce knockback effect
        self.knockback_velocity[0] *= 0.9
        self.knockback_velocity[1] *= 0.9

    def update(self, player_x, player_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Update spider position and animation

        Args:
            player_x (int): Player's x position
            player_y (int): Player's y position
            collision_handler: Optional collision handler for collision detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Skip updates if dead
        if self.is_dead:
            return

        # Update timers
        self._update_timers()

        # Initialize float position if not already set
        if self.float_x == 0.0 and self.float_y == 0.0:
            self.float_x = float(self.rect.x)
            self.float_y = float(self.rect.y)

        # Check if being knocked back
        if self.is_knocked_back:
            # Update knockback movement
            self._update_knockback(collision_handler, tile_mapping, map_data)

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

            # Check if player is within detection range
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
                        self._move_towards_player(player_x, player_y, collision_handler, tile_mapping, map_data)

                        # Update float position based on velocity
                        self.float_x += self.velocity[0]
                        self.float_y += self.velocity[1]

                        # Update rect position from float position
                        self.rect.x = int(self.float_x)
                        self.rect.y = int(self.float_y)
                else:
                    # If no collision data, use default movement
                    self._move_towards_player(player_x, player_y, collision_handler, tile_mapping, map_data)

                    # Update float position based on velocity
                    self.float_x += self.velocity[0]
                    self.float_y += self.velocity[1]

                    # Update rect position from float position
                    self.rect.x = int(self.float_x)
                    self.rect.y = int(self.float_y)
            else:
                # Player is outside detection range, stop moving and set to idle
                self.velocity = [0, 0]
                self.state = "idle"
                self.path = []  # Clear any existing path

        # Make sure we're using the correct animation state based on velocity
        if not self.is_hit and not self.is_dying and not self.is_knocked_back:
            if self.velocity[0] == 0 and self.velocity[1] == 0:
                self.state = "idle"
            else:
                self.state = "run"

        # Update animation
        self.update_animation()

    def _update_timers(self):
        """Update all timers"""
        # Update damage cooldown
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1

        # Update hit timer
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0 and self.is_hit:
                self.is_hit = False
                self.state = "idle"

        # Update death timer
        if self.death_timer > 0:
            self.death_timer -= 1
            # Check if death timer has expired and we're still dying
            if self.death_timer <= 0 and self.is_dying:
                # Mark as dead so the enemy manager will remove it
                self.is_dead = True
                # Keep the is_dying flag true until removed
                # This ensures the death animation continues to display

        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= 1
            if self.health_bar_timer <= 0:
                self.show_health_bar = False

    def _update_death_animation(self, animation_key):
        """Update death animation

        Args:
            animation_key (str): The animation key for the death animation
        """
        # Calculate which frame to show based on death timer
        total_frames = len(self.sprites[animation_key])

        # Calculate current frame based on death timer
        if self.death_timer > 0:
            progress = 1.0 - (self.death_timer / self.death_duration)
            self.death_frame = min(int(progress * total_frames), total_frames - 1)
        else:
            # If death timer expired, mark as dead and use the last frame
            self.is_dead = True
            self.death_frame = total_frames - 1

        # Use death frame for rendering
        if self.death_frame < total_frames:
            self.image = self.sprites[animation_key][self.death_frame]

    def update_animation(self):
        """Update the spider's animation frame"""
        # Handle death animation
        if self.is_dying:
            # Use death animation
            current_animation_key = f"death_{self.direction}"
            # Fallback to idle if death animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        # Handle hit animation
        elif self.is_hit:
            # Use hit animation
            current_animation_key = f"hit_{self.direction}"
            # Fallback to idle if hit animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        # Handle run animation when moving
        elif self.state == "run" and (self.velocity[0] != 0 or self.velocity[1] != 0):
            # Use run animation
            current_animation_key = f"run_{self.direction}"
            # Fallback to idle if run animation doesn't exist
            if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
                current_animation_key = f"idle_{self.direction}"
        else:
            # Force idle animation when not moving or state is idle
            if self.state != "idle":
                self.state = "idle"  # Ensure state is set to idle
                self.animation_timer = 0  # Reset animation timer
                self.frame = 0  # Reset animation frame
            current_animation_key = f"idle_{self.direction}"

        # Check if the animation exists
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            # Try the right direction if this one doesn't exist
            if current_animation_key.startswith("death_"):
                current_animation_key = "death_right"
            elif current_animation_key.startswith("hit_"):
                current_animation_key = "hit_right"
            else:
                current_animation_key = "idle_right"

            # If we still don't have a valid animation, try fallbacks
            if (current_animation_key.startswith("death_") and
                (current_animation_key not in self.sprites or not self.sprites[current_animation_key])):
                current_animation_key = "idle_right"

        # If we still don't have a valid animation, return
        if current_animation_key not in self.sprites or not self.sprites[current_animation_key]:
            return

        # Special handling for death animation
        if self.is_dying and current_animation_key.startswith("death_"):
            self._update_death_animation(current_animation_key)
            return

        # Update animation frame for non-death animations
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            # Ensure we have a valid animation list
            if current_animation_key in self.sprites and self.sprites[current_animation_key]:
                # Reset frame if it's out of range (this can happen when switching animations)
                if self.frame >= len(self.sprites[current_animation_key]):
                    self.frame = 0
                # Update to next frame
                self.frame = (self.frame + 1) % len(self.sprites[current_animation_key])

        # Update image - with safety checks
        if (current_animation_key in self.sprites and
            self.sprites[current_animation_key] and
            self.frame < len(self.sprites[current_animation_key])):
            self.image = self.sprites[current_animation_key][self.frame]

    def draw(self, surface, camera_x=0, camera_y=0, zoom_factor=1.0):
        """Draw the spider

        Args:
            surface (pygame.Surface): The surface to draw on
            camera_x (int): Camera x offset
            camera_y (int): Camera y offset
            zoom_factor (float): Zoom factor for scaling
        """
        # Skip drawing if dead (but not if dying - we want to show the death animation)
        if self.is_dead and not self.is_dying:
            return

        # Calculate position with camera offset
        # Keep logical coordinates, only scale for visual representation
        logical_draw_x = self.rect.x - camera_x
        logical_draw_y = self.rect.y - camera_y

        # Scale the screen position for zoom
        draw_x = logical_draw_x * zoom_factor
        draw_y = logical_draw_y * zoom_factor

        # Scale the image if zoom factor is not 1.0
        if zoom_factor != 1.0:
            # Calculate new size based on zoom factor
            original_size = self.image.get_size()
            new_width = int(original_size[0] * zoom_factor)
            new_height = int(original_size[1] * zoom_factor)
            scaled_image = pygame.transform.scale(self.image, (new_width, new_height))
            # Draw the scaled spider
            surface.blit(scaled_image, (draw_x, draw_y))
        else:
            # Draw the spider at normal size
            draw_rect = pygame.Rect(draw_x, draw_y, self.rect.width, self.rect.height)
            surface.blit(self.image, draw_rect)

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

            # Calculate width of health indicator based on percentage
            health_width = int(health_bar_width * health_percent)

            if health_width > 0:
                try:
                    # Create a subsurface of the background with the appropriate width
                    health_rect = pygame.Rect(0, 0, health_width, self.health_bar_bg.get_height())
                    health_bg_part = self.health_bar_bg.subsurface(health_rect)

                    # Draw the health background
                    surface.blit(health_bg_part, (screen_x, screen_y))

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))
                except ValueError:
                    # If subsurface fails, use clipping rect
                    clip_rect = surface.get_clip()

                    health_clip_rect = pygame.Rect(
                        screen_x,
                        screen_y,
                        health_width,
                        self.health_bar_bg.get_height()
                    )

                    # Draw with clipping
                    surface.set_clip(health_clip_rect)
                    surface.blit(self.health_bar_bg, (screen_x, screen_y))
                    surface.set_clip(clip_rect)

                    # Draw the health indicator on top
                    surface.blit(self.health_indicator, (screen_x, screen_y))

    def apply_knockback(self, direction_x, direction_y, collision_handler=None, tile_mapping=None, map_data=None):
        """Override the base apply_knockback method to preserve the original direction

        Args:
            direction_x (float): X component of knockback direction
            direction_y (float): Y component of knockback direction
            collision_handler: Optional collision handler for wall detection
            tile_mapping: Optional tile mapping for collision detection
            map_data: Optional map data for collision detection
        """
        # Store the original direction
        original_direction = self.direction

        # Call the parent class method to apply knockback
        result = super().apply_knockback(direction_x, direction_y, collision_handler, tile_mapping, map_data)

        # Restore the original direction
        self.direction = original_direction

        return result

    def take_damage(self, damage_amount=10, knockback_x=0, knockback_y=0, collision_handler=None, tile_mapping=None, map_data=None):
        """Apply damage to the spider and trigger hit animation

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

        # Store the original direction before applying damage
        original_direction = self.direction

        # Reduce health
        self.current_health -= damage_amount

        # Show health bar
        self.show_health_bar = True
        self.health_bar_timer = self.health_bar_duration

        # Start damage cooldown to prevent multiple hits from a single attack
        self.damage_cooldown = self.damage_cooldown_time

        # Check if spider should die
        if self.current_health <= 0:
            self.current_health = 0
            # Ensure the direction is preserved for death animation
            self.direction = original_direction
            self.start_death_animation()
            return True

        # Apply knockback if direction is provided
        if knockback_x != 0 or knockback_y != 0:
            # Normalize the knockback direction
            distance = ((knockback_x ** 2) + (knockback_y ** 2)) ** 0.5
            if distance > 0:
                # Scale knockback by a factor
                knockback_factor = min(distance, 10) / distance
                normalized_x = (knockback_x / distance) * knockback_factor * self.knockback_strength
                normalized_y = (knockback_y / distance) * knockback_factor * self.knockback_strength

                # Use our overridden apply_knockback method which preserves direction
                self.apply_knockback(normalized_x, normalized_y, collision_handler, tile_mapping, map_data)
            else:
                # Fallback if direction is invalid
                self.apply_knockback(knockback_x, knockback_y, collision_handler, tile_mapping, map_data)

        # Ensure the direction is preserved after knockback
        self.direction = original_direction

        # Start hit animation
        self.start_hit_animation()
        return True

    def start_hit_animation(self):
        """Start the hit animation sequence"""
        self.is_hit = True
        self.hit_timer = self.hit_duration
        self.animation_timer = 0
        self.state = "hit"

    def start_death_animation(self):
        """Start the death animation sequence"""
        self.is_dying = True
        self.is_hit = False  # Cancel any hit animation
        self.death_timer = self.death_duration
        self.death_frame = 0  # Reset death frame
        self.animation_timer = 0
        self.state = "death"
        self.velocity = [0, 0]  # Stop movement

        # Always use the right direction for death animation for consistency
        self.direction = "right"

        # Force the current frame to be the first frame of the death animation
        death_key = "death_right"
        if death_key in self.sprites and self.sprites[death_key]:
            self.image = self.sprites[death_key][0]

    def apply_knockback_to_player(self, player, **_):
        """Apply knockback to the player when colliding

        Args:
            player: The player object to apply knockback to
            **_: Additional parameters (ignored for compatibility with enemy manager)
        """
        # Skip if on cooldown, hit, dying or dead
        if self.damage_cooldown > 0 or self.is_hit or self.is_dying or self.is_dead:
            return False

        # Check if we're colliding with the player
        if self.rect.colliderect(player.rect):
            # Calculate knockback direction (away from spider)
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            # Apply knockback to the player
            if hasattr(player, 'apply_knockback'):
                player.apply_knockback(dx, dy)

            # Apply damage to the player
            if hasattr(player, 'take_damage'):
                player.take_damage(10)  # Spider deals 10 damage

            # Start cooldown
            self.damage_cooldown = self.damage_cooldown_time

            return True
        return False