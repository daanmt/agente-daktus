"""
Agent V2 CLI Entry Point

This is the main entry point for the Agent V2 CLI.
It simply delegates to the CLI module.
"""

import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import and run CLI
try:
    from cli.run_qa_cli import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ Error importing CLI: {e}")
    print(f"Make sure src/cli/run_qa_cli.py exists")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n❌ Cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

