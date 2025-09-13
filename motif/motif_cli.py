#!/usr/bin/env python3
"""
MOTIF Command Line Interface
Entry point for the MOTIF programming language
"""

import sys
import os
from motif.parser import interpret_motif


def main():
    """Main entry point for the motif command"""
    if len(sys.argv) < 2:
        print("Usage: motif <script.motif>")
        print("       motif --help")
        sys.exit(1)
    
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("MOTIF: The First AI-Native Musical Programming Language")
        print()
        print("Usage:")
        print("  motif <script.motif>    Execute a MOTIF script")
        print("  motif --help           Show this help message")
        print()
        print("Examples:")
        print("  motif examples/basic_despair.motif")
        print("  motif examples/ml_enhanced_nostalgia.motif")
        print()
        print("For more information, visit: https://github.com/your-repo/motif")
        sys.exit(0)
    
    script_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(script_path):
        print(f"Error: File '{script_path}' not found")
        sys.exit(1)
    
    # Read and execute the MOTIF script
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            motif_code = f.read()
        
        print(f"🎵 Executing MOTIF script: {script_path}")
        print("=" * 60)
        
        result = interpret_motif(motif_code)
        
        print("\n" + "=" * 60)
        print("✅ MOTIF execution completed successfully!")
        
        if result and isinstance(result, dict):
            print(f"📊 Final result: {result.get('status', 'completed')}")
        
    except FileNotFoundError:
        print(f"Error: File '{script_path}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading '{script_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error executing MOTIF script: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
