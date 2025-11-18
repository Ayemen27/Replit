"""Initialize bridge configuration"""

import shutil
from pathlib import Path


def run_init():
    """Initialize bridge tool configuration"""
    
    print("="* 60)
    print("Bridge Tool - Initialization")
    print("="* 60)
    
    config_file = "bridge.config.yaml"
    example_file = "bridge.config.example.yaml"
    
    # Check if config already exists
    if Path(config_file).exists():
        print(f"\n⚠️  {config_file} already exists!")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Initialization cancelled")
            return
    
    # Copy example config
    if not Path(example_file).exists():
        print(f"\n✗ {example_file} not found!")
        return
    
    try:
        shutil.copy(example_file, config_file)
        print(f"\n✓ Created {config_file}")
        print("\nNext steps:")
        print(f"1. Edit {config_file} with your server details:")
        print("   - Server hostname/IP")
        print("   - SSH username")
        print("   - SSH key path or password")
        print("   - Remote paths")
        print("\n2. Test connection:")
        print("   python3 bridge_tool/cli.py test")
        print("\n3. Deploy:")
        print("   python3 bridge_tool/cli.py push --dry-run  # Test first")
        print("   python3 bridge_tool/cli.py push            # Actual deployment")
        
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
