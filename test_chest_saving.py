#!/usr/bin/env python3
"""
Test script to verify chest inventory saving functionality
"""

import json
import os
from pathlib import Path

def check_chest_contents_in_maps():
    """Check if chest contents are being saved in map files"""
    print("🔍 Checking chest contents in map files...")
    
    maps_dir = Path("Maps")
    if not maps_dir.exists():
        print("❌ Maps directory not found!")
        return
    
    found_chest_data = False
    
    # Check all JSON files in Maps directory
    for json_file in maps_dir.rglob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Check if this file has game_state with chest_contents
            if "game_state" in data and "chest_contents" in data["game_state"]:
                chest_contents = data["game_state"]["chest_contents"]
                
                if chest_contents:  # If not empty
                    print(f"📦 Found chest contents in {json_file}:")
                    for chest_pos, contents in chest_contents.items():
                        print(f"  Chest at {chest_pos}: {len(contents)} items")
                        for slot, item in contents.items():
                            print(f"    Slot {slot}: {item}")
                    found_chest_data = True
                else:
                    print(f"📭 Empty chest_contents in {json_file}")
                    
        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")
    
    if not found_chest_data:
        print("📭 No chest contents found in any map files")
    
    return found_chest_data

def check_character_inventory():
    """Check character inventory save file"""
    print("\n🎒 Checking character inventory...")
    
    inventory_file = Path("SaveData/character_inventory.json")
    if not inventory_file.exists():
        print("❌ Character inventory file not found!")
        return False
    
    try:
        with open(inventory_file, 'r') as f:
            data = json.load(f)
        
        inventory = data.get("inventory", [])
        non_empty_items = [item for item in inventory if item is not None]
        
        print(f"🎒 Character inventory has {len(non_empty_items)} items:")
        for i, item in enumerate(inventory):
            if item:
                print(f"  Slot {i}: {item}")
        
        return len(non_empty_items) > 0
        
    except Exception as e:
        print(f"❌ Error reading character inventory: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Inventory Saving System")
    print("=" * 50)
    
    # Check character inventory
    has_character_items = check_character_inventory()
    
    # Check chest contents
    has_chest_items = check_chest_contents_in_maps()
    
    print("\n📊 Summary:")
    print(f"Character inventory has items: {'✅' if has_character_items else '❌'}")
    print(f"Chest contents found: {'✅' if has_chest_items else '❌'}")
    
    print("\n💡 To test chest saving:")
    print("1. Run the game")
    print("2. Open a chest")
    print("3. Put some items in the chest")
    print("4. Close the chest (ESC key)")
    print("5. Run this script again to check if items were saved")
    
    print("\n🔧 Expected behavior:")
    print("- Items collected should appear in character inventory")
    print("- Items put in chests should appear in map file chest_contents")
    print("- Debug output should show the saving process")

if __name__ == "__main__":
    main()
