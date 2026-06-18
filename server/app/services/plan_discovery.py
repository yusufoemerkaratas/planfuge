from pathlib import Path


def discover_plans(project_root: Path) -> list[str]:
    pages_dir = project_root / "data" / "pages"
    if not pages_dir.exists() or not pages_dir.is_dir():
        return []
    
    plans = []
    for file_path in pages_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".png":
            plans.append(file_path.stem)
            
    return sorted(plans)
