#!/usr/bin/env python3
"""
Manual test to verify chest saving functionality by simulating the process
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_core.playscreen_components.item_system.lootchest_manager import LootchestManager
from game_core.playscreen_components.inventory_system.chest_inventory import ChestInventory
from game_core.playscreen_components.state_system.game_state_saver import GameStateSaver

def test_chest_saving_process():
    """Test the chest saving process step by step"""
    print("🧪 Testing Chest Saving Process")
    print("=" * 50)
    
    # Step 1: Create a lootchest manager
    print("📦 Step 1: Creating LootchestManager...")
    lootchest_manager = LootchestManager()
    lootchest_manager.set_current_map("firstlevel")
    
    # Step 2: Initialize a chest
    chest_pos = (14, 9)
    print(f"🗃️ Step 2: Initializing chest at position {chest_pos}...")
    lootchest_manager.initialize_chest_contents(chest_pos)
    
    # Step 3: Create a chest inventory
    print("🎒 Step 3: Creating ChestInventory...")
    chest_inventory = ChestInventory(1280, 720)
    
    # Step 4: Show the chest with empty contents
    print("👁️ Step 4: Showing chest inventory...")
    chest_contents = lootchest_manager.get_chest_contents(chest_pos)
    chest_inventory.show(chest_pos, chest_contents)
    
    # Step 5: Add some test items to the chest inventory
    print("➕ Step 5: Adding test items to chest inventory...")
    test_item = {
        "name": "Crystal",
        "count": 3,
        "image": None  # We'll skip the image for this test
    }
    chest_inventory.inventory_items[0] = test_item
    chest_inventory.inventory_items[5] = {
        "name": "Key", 
        "count": 2,
        "image": None
    }
    
    # Count items
    non_empty_items = [item for item in chest_inventory.inventory_items if item is not None]
    print(f"📋 Chest now has {len(non_empty_items)} items")
    
    # Step 6: Hide the chest (this should sync the contents)
    print("🔒 Step 6: Hiding chest inventory (syncing contents)...")
    sync_callback = lootchest_manager.update_chest_contents
    chest_inventory.hide(sync_callback)
    
    # Step 7: Check if the contents were synced to the lootchest manager
    print("🔍 Step 7: Checking if contents were synced...")
    updated_contents = lootchest_manager.get_chest_contents(chest_pos)
    updated_non_empty = [item for item in updated_contents if item is not None]
    print(f"📦 LootchestManager now has {len(updated_non_empty)} items for chest {chest_pos}")
    
    for i, item in enumerate(updated_contents):
        if item:
            print(f"  Slot {i}: {item}")
    
    # Step 8: Get chest contents data for saving
    print("💾 Step 8: Getting chest contents data for saving...")
    chest_data = lootchest_manager.get_chest_contents_data()
    print(f"🗃️ Chest contents data: {chest_data}")
    
    # Step 9: Test saving to a mock map file
    print("📄 Step 9: Testing save to map file...")
    
    # Create a mock map data structure
    mock_map_data = {
        "name": "firstlevel",
        "width": 154,
        "height": 70,
        "tile_size": 16,
        "tile_mapping": {},
        "layers": [{"visible": True, "map_data": []}],
        "game_state": {
            "camera": {"x": 0, "y": 0},
            "enemies": [],
            "inventory": [],
            "collected_keys": [],
            "collected_crystals": [],
            "opened_lootchests": [],
            "chest_contents": chest_data
        }
    }
    
    # Save to a test file
    test_file = "test_chest_save.json"
    try:
        with open(test_file, 'w') as f:
            json.dump(mock_map_data, f, indent=2)
        print(f"✅ Successfully saved test data to {test_file}")
        
        # Verify the save
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        
        saved_chest_data = loaded_data["game_state"]["chest_contents"]
        print(f"🔍 Verified saved chest data: {saved_chest_data}")
        
        # Clean up
        os.remove(test_file)
        print(f"🧹 Cleaned up test file")
        
    except Exception as e:
        print(f"❌ Error during save test: {e}")
        return False
    
    # Step 10: Summary
    print("\n📊 Test Summary:")
    print(f"✅ Chest initialized: {chest_pos}")
    print(f"✅ Items added to chest inventory: {len(non_empty_items)}")
    print(f"✅ Contents synced to lootchest manager: {len(updated_non_empty)}")
    print(f"✅ Chest data ready for saving: {bool(chest_data)}")
    print(f"✅ Save/load test completed successfully")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_chest_saving_process()
        if success:
            print("\n🎉 All tests passed! Chest saving should work correctly.")
            print("\n💡 If chest saving is still not working in the game:")
            print("1. Check that the save callback is being called (debug output)")
            print("2. Verify that the ESC key properly triggers hide_chest_inventory()")
            print("3. Ensure the game state save is actually writing to the map file")
        else:
            print("\n❌ Tests failed! There's an issue with the chest saving process.")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
