"""
Debug utilities for the game
"""

class DebugManager:
    """Manages debug output for the game"""

    # Singleton instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the debug manager"""
        self.debug_enabled = False
        self.debug_categories = {
            "enemy": False,
            "player": False,
            "collision": False,
            "animation": False,
            "map": False,
            "editor": False,
            "performance": False,
            "item": False
        }

    def enable_debug(self, enable=True):
        """Enable or disable debug output"""
        self.debug_enabled = enable

    def enable_category(self, category, enable=True):
        """Enable or disable a specific debug category"""
        if category in self.debug_categories:
            self.debug_categories[category] = enable

    def log(self, message, category=None):
        """Log a debug message if debugging is enabled"""
        # Quick return if debugging is disabled
        if not self.debug_enabled:
            return

        # Check if the category is enabled or if no category is specified
        if category is None or (category in self.debug_categories and self.debug_categories[category]):
            print(f"[DEBUG:{category if category else 'GENERAL'}] {message}")

    def is_category_enabled(self, category):
        """Check if a specific debug category is enabled"""
        # Quick return if debugging is disabled
        if not self.debug_enabled:
            return False

        # Check if the category exists and is enabled
        return category in self.debug_categories and self.debug_categories[category]

# Create a global instance for easy access
debug_manager = DebugManager()
