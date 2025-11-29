"""
Agent V2 CLI - Simple Command Line Interface

This CLI uses ONLY the Agent V2 pipeline.
No legacy code, no fallbacks.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# CRITICAL: Load .env FIRST, before any other imports
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

# Calculate project root: src/cli/run_qa_cli.py -> project root
project_root = Path(__file__).resolve().parent.parent.parent
env_file = project_root / ".env"

# Load .env from project root
if env_file.exists():
    load_dotenv(env_file, override=True)
else:
    # Fallback: try current working directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env, override=True)
    else:
        load_dotenv(override=True)

# Add src to path AFTER loading .env
current_dir = project_root
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import Agent V2 pipeline
try:
    from agent_v2.pipeline import analyze
    from agent_v2.logger import logger
except ImportError as e:
    print(f"ERROR: Error importing Agent V2: {e}")
    print(f"Make sure you're running from the project root")
    sys.exit(1)


def print_header():
    """Print CLI header"""
    print("\n" + "=" * 60)
    print("AGENT V2 - Clinical Protocol Analysis")
    print("=" * 60 + "\n")


def list_files(directory: str, extension: str) -> list[Path]:
    """List files in directory with extension (relative to project root)"""
    # Use project root as base for relative paths
    if Path(directory).is_absolute():
        path = Path(directory)
    else:
        # Relative to project root
        path = project_root / directory
    
    if not path.exists():
        return []
    return sorted(path.glob(f"*{extension}"))


def select_protocol() -> Optional[str]:
    """Select protocol file"""
    print("PROTOCOL SELECTION")
    print("-" * 60)
    
    protocols = list_files("models_json", ".json")
    
    if not protocols:
        models_path = project_root / "models_json"
        print(f"ERROR: No protocol files found in models_json/")
        print(f"  Looking in: {models_path}")
        print(f"  Directory exists: {models_path.exists()}")
        if models_path.exists():
            all_files = list(models_path.iterdir())
            print(f"  Files in directory: {len(all_files)}")
            for f in all_files[:5]:
                print(f"    - {f.name}")
        return None
    
    for i, proto in enumerate(protocols, 1):
        print(f"  {i}. {proto.name}")
    
    while True:
        try:
            choice = input("\nSelect protocol number: ").strip()
            idx = int(choice) - 1
            
            if 0 <= idx < len(protocols):
                selected = str(protocols[idx])
                print(f"Selected: {protocols[idx].name}\n")
                return selected
            else:
                print("ERROR: Invalid number")
        except ValueError:
            print("ERROR: Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled")
            sys.exit(0)


def select_playbook() -> Optional[str]:
    """Select playbook file"""
    print("PLAYBOOK SELECTION")
    print("-" * 60)
    
    playbooks = list_files("models_json", ".md")
    playbooks.extend(list_files("models_json", ".pdf"))
    
    if not playbooks:
        print("WARNING: No playbook files found in models_json/")
        print("   Analysis will be structural only\n")
        return None
    
    for i, pb in enumerate(playbooks, 1):
        print(f"  {i}. {pb.name}")
    print(f"  0. None (structural analysis only)")
    
    while True:
        try:
            choice = input("\nSelect playbook number (0 for none): ").strip()
            
            if choice == "0":
                print("No playbook selected - structural analysis only\n")
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(playbooks):
                selected = str(playbooks[idx])
                print(f"Selected: {playbooks[idx].name}\n")
                return selected
            else:
                print("ERROR: Invalid number")
        except ValueError:
            print("ERROR: Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled")
            sys.exit(0)


def select_model() -> str:
    """Select LLM model"""
    print("MODEL SELECTION")
    print("-" * 60)
    
    # Available models
    models = [
        ("anthropic/claude-sonnet-4.5", "Claude Sonnet 4.5 (Recommended)"),
        ("google/gemini-2.5-flash-preview-09-2025", "Gemini 2.5 Flash Preview"),
        ("openai/gpt-5-mini", "GPT-5 Mini"),
        ("google/gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite"),
        ("google/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("google/gemini-2.5-pro", "Gemini 2.5 Pro"),
        ("anthropic/claude-sonnet-4", "Claude Sonnet 4"),
        ("openai/gpt-4.1-mini", "GPT-4.1 Mini"),
        ("google/gemini-2.0-flash-001", "Gemini 2.0 Flash"),
        ("openai/gpt-4o-mini", "GPT-4o Mini"),
        ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
        ("x-ai/grok-2-1212", "Grok 2"),
    ]
    
    for i, (model_id, description) in enumerate(models, 1):
        print(f"  {i}. {description}")
    print(f"  0. Default (Google Gemini 2.5 Flash Preview)")
    
    while True:
        try:
            choice = input("\nSelect model number (0 for default): ").strip()
            
            if choice == "0" or choice == "":
                model_id = "google/gemini-2.5-flash-preview-09-2025"
                print(f"Using default: Google Gemini 2.5 Flash Preview\n")
                return model_id
            
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                model_id = models[idx][0]
                print(f"Selected: {models[idx][1]}\n")
                return model_id
            else:
                print("ERROR: Invalid number")
        except ValueError:
            print("ERROR: Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled")
            sys.exit(0)


def save_report(result: dict, protocol_name: str, project_root: Path):
    """Save analysis report"""
    from datetime import datetime
    import json
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Save JSON
    json_path = reports_dir / f"{protocol_name}_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Save text report
    txt_path = reports_dir / f"{protocol_name}_{timestamp}.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("AGENT V2 - PROTOCOL ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        # Metadata
        metadata = result.get("metadata", {})
        f.write("METADATA\n")
        f.write("-" * 60 + "\n")
        f.write(f"Protocol: {metadata.get('protocol_path', 'N/A')}\n")
        f.write(f"Playbook: {metadata.get('playbook_path', 'None')}\n")
        f.write(f"Model: {metadata.get('model_used', 'N/A')}\n")
        f.write(f"Timestamp: {metadata.get('timestamp', 'N/A')}\n")
        f.write(f"Processing Time: {metadata.get('processing_time_ms', 0)}ms\n\n")
        
        # Improvement Suggestions
        improvements = result.get("improvement_suggestions", [])
        f.write("IMPROVEMENT SUGGESTIONS\n")
        f.write("-" * 60 + "\n")
        if improvements:
            for i, imp in enumerate(improvements, 1):
                f.write(f"{i}. [{imp.get('priority', 'N/A')}] {imp.get('description', 'N/A')}\n")
        else:
            f.write("No improvement suggestions.\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("Full JSON report saved to: " + str(json_path) + "\n")
        f.write("=" * 60 + "\n")
    
    return json_path, txt_path


def main():
    """Main CLI function"""
    print_header()
    
    try:
        # Step 1: Select protocol
        protocol_path = select_protocol()
        if not protocol_path:
            print("ERROR: Protocol selection required")
            sys.exit(1)
        
        # Step 2: Select playbook
        playbook_path = select_playbook()
        
        # Step 3: Select model
        model = select_model()
        
        # Step 4: Confirm
        print("CONFIGURATION")
        print("-" * 60)
        print(f"Protocol: {Path(protocol_path).name}")
        print(f"Playbook: {Path(playbook_path).name if playbook_path else 'None'}")
        print(f"Model: {model}")
        print(f"Log: {logger.get_log_path()}\n")
        
        # Step 5: Run analysis
        print("RUNNING ANALYSIS")
        print("-" * 60)
        print("This may take a few moments...\n")
        
        result = analyze(
            protocol_path=protocol_path,
            playbook_path=playbook_path,
            model=model
        )
        
        # Step 6: Save reports
        protocol_name = Path(protocol_path).stem
        json_path, txt_path = save_report(result, protocol_name, project_root)
        
        # Step 7: Show summary
        print("ANALYSIS COMPLETE")
        print("-" * 60)
        improvements_count = len(result.get('improvement_suggestions', []))
        print(f"Improvement Suggestions: {improvements_count}")
        print(f"\nReports saved:")
        print(f"   JSON: {json_path}")
        print(f"   Text: {txt_path}")
        print(f"   Log:  {logger.get_log_path()}\n")
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print(f"Check log file: {logger.get_log_path()}")
        sys.exit(1)


if __name__ == "__main__":
    main()

