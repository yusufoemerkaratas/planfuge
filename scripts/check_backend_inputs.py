import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InputCheck:
    path: Path
    exists: bool
    required: bool
    description: str
    expected_kind: str = "file"

    @property
    def level(self) -> str:
        if self.exists:
            return "OK"

        if self.required:
            return "ERROR"

        return "WARN"


@dataclass(frozen=True)
class InputCheckResult:
    plan_id: str
    checks: list[InputCheck]

    @property
    def exit_code(self) -> int:
        has_missing_required_file = any(check.required and not check.exists for check in self.checks)
        return 1 if has_missing_required_file else 0


def check_backend_inputs(project_root: Path, plan_id: str) -> InputCheckResult:
    checks = [
        build_check(project_root, Path(f"data/pages/{plan_id}.png"), True, "rendered plan image", "file"),
        build_check(
            project_root,
            Path(f"data/metadata/{plan_id}_metadata.json"),
            False,
            "plan metadata",
        ),
        build_check(
            project_root,
            Path(f"outputs/candidates/{plan_id}_candidates.json"),
            False,
            "candidate JSON",
        ),
        build_check(
            project_root,
            Path(f"outputs/overlays/{plan_id}_overlay.png"),
            False,
            "CV overlay image",
        ),
        build_check(project_root, Path("outputs/exports"), False, "export directory", "directory"),
    ]
    return InputCheckResult(plan_id=plan_id, checks=checks)


def build_check(
    project_root: Path,
    relative_path: Path,
    required: bool,
    description: str,
    expected_kind: str = "file",
) -> InputCheck:
    absolute_path = project_root / relative_path
    exists = absolute_path.is_dir() if expected_kind == "directory" else absolute_path.is_file()
    return InputCheck(
        path=relative_path,
        exists=exists,
        required=required,
        description=description,
        expected_kind=expected_kind,
    )


def format_report(result: InputCheckResult) -> str:
    lines = [f"Backend input check for {result.plan_id}"]
    for check in result.checks:
        requirement = "required" if check.required else "optional"
        lines.append(f"[{check.level}] {check.path} ({requirement}: {check.description})")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check backend demo input files for a plan.")
    parser.add_argument("--plan-id", required=True, help="Plan id, for example SP_U1_0003.")
    parser.add_argument(
        "--project-root",
        default=Path.cwd(),
        type=Path,
        help="Project root. Defaults to the current working directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = check_backend_inputs(args.project_root, args.plan_id)
    print(format_report(result))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
