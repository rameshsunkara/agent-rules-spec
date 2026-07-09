#!/usr/bin/env python3
"""Validate schemas, examples, indexes, and conformance fixtures."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from yaml.constructor import ConstructorError
from yaml.events import AliasEvent


ROOT = Path(__file__).resolve().parents[1]
KNOWN_FIELDS = {
    "spec-version",
    "name",
    "description",
    "activation",
    "paths",
    "keywords",
    "priority",
    "tags",
}
LEGACY_FIELDS = (KNOWN_FIELDS - {"activation"}) | {"trigger"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Small YAML 1.2 loader for rule frontmatter and fixtures."""

    def compose_node(self, parent: Any, index: Any) -> Any:
        event = self.peek_event()
        if (
            isinstance(event, AliasEvent)
            or getattr(event, "anchor", None)
            or getattr(event, "tag", None) is not None
        ):
            raise ConstructorError(
                "while composing YAML",
                getattr(event, "start_mark", None),
                "anchors, aliases, and explicit tags are not supported",
                getattr(event, "start_mark", None),
            )
        return super().compose_node(parent, index)


UniqueKeyLoader.yaml_implicit_resolvers = {
    key: list(resolvers)
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for first_character, resolvers in UniqueKeyLoader.yaml_implicit_resolvers.items():
    UniqueKeyLoader.yaml_implicit_resolvers[first_character] = [
        (tag, pattern)
        for tag, pattern in resolvers
        if tag
        not in {
            "tag:yaml.org,2002:bool",
            "tag:yaml.org,2002:float",
            "tag:yaml.org,2002:int",
            "tag:yaml.org,2002:null",
            "tag:yaml.org,2002:timestamp",
        }
    ]
UniqueKeyLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$"),
    list("tf"),
)
UniqueKeyLoader.add_implicit_resolver(
    "tag:yaml.org,2002:int",
    re.compile(r"^[-+]?(?:0|[1-9][0-9]*)$"),
    list("-+0123456789"),
)
UniqueKeyLoader.add_implicit_resolver(
    "tag:yaml.org,2002:null",
    re.compile(r"^(?:~|null|)$"),
    ["~", "n", None],
)
UniqueKeyLoader.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(
        r"^[-+]?(?:(?:0|[1-9][0-9]*)\.[0-9]+"
        r"(?:[eE][-+]?[0-9]+)?|"
        r"(?:0|[1-9][0-9]*)[eE][-+]?[0-9]+)$"
    ),
    list("-+0123456789"),
)


def construct_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "merge keys are not supported",
                key_node.start_mark,
            )
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "mapping keys must be strings",
                key_node.start_mark,
            )
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)


def load_yaml(path: Path) -> Any:
    return yaml.load(read_utf8(path), Loader=UniqueKeyLoader)


def decode_utf8(data: bytes, source: str) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{source}: UTF-8 byte-order marks are not supported")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{source}: invalid UTF-8") from exc


def read_utf8(path: Path) -> str:
    return decode_utf8(path.read_bytes(), str(path))


def parse_rule_text(text: str) -> tuple[dict[str, Any] | None, str]:
    if text.startswith("\ufeff"):
        raise ValueError("UTF-8 byte-order marks are not supported")
    if not text.startswith(("---\n", "---\r\n")):
        return None, text

    match = re.match(r"\A---\r?\n(?P<frontmatter>.*?)^---\r?\n", text, re.DOTALL | re.MULTILINE)
    if match is None:
        raise ValueError("unclosed frontmatter")

    raw_frontmatter = match.group("frontmatter")
    frontmatter = yaml.load(raw_frontmatter, Loader=UniqueKeyLoader)
    if frontmatter is None:
        frontmatter = {}
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a mapping")
    return frontmatter, text[match.end() :]


def load_schema(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def versioned_diagnostics(frontmatter: dict[str, Any]) -> list[str]:
    activation = frontmatter.get("activation")
    paths = frontmatter.get("paths")
    keywords = frontmatter.get("keywords")

    if "trigger" in frontmatter:
        return ["legacy-trigger-not-allowed"]
    if activation is None:
        return ["activation-required"]
    if activation not in {"always", "on-match", "manual"}:
        return ["invalid-activation"]
    if activation == "always" and (paths is not None or keywords is not None):
        return ["always-with-condition"]
    if activation == "on-match" and paths is None and keywords is None:
        return ["on-match-missing-condition"]
    if activation == "on-match" and paths is not None and keywords is not None:
        return ["paths-keywords-combination-unresolved"]
    if activation == "manual" and keywords is not None:
        return ["manual-keywords-invalid"]

    path_pattern = re.compile(
        r"^(?![!/])(?!.*//)(?!.*(?:^|/)\.{1,2}(?:/|$))"
        r"(?!.*\/$)(?!.*[{}\[\]\\]).+$"
    )
    if paths is not None and (
        not isinstance(paths, list)
        or any(not isinstance(path, str) or not path_pattern.match(path) for path in paths)
    ):
        return ["invalid-path-pattern"]

    diagnostics: list[str] = []
    if keywords is not None:
        diagnostics.append("experimental-keywords")
    if "priority" in frontmatter:
        diagnostics.append("advisory-priority")

    for field in frontmatter:
        if field in KNOWN_FIELDS:
            continue
        diagnostics.append(
            "unknown-extension-namespace"
            if field.startswith("x-")
            else "unknown-unprefixed-field"
        )
    return diagnostics


def normalize_rule(
    frontmatter: dict[str, Any] | None,
    rule_validator: Draft202012Validator,
) -> tuple[bool, dict[str, Any] | None, list[str]]:
    if frontmatter is None:
        return True, {"spec-version": 1, "activation": "always"}, []

    if "spec-version" in frontmatter:
        if type(frontmatter["spec-version"]) is not int or frontmatter["spec-version"] != 1:
            return False, None, ["unsupported-spec-version"]
        diagnostics = versioned_diagnostics(frontmatter)
        valid = rule_validator.is_valid(frontmatter)
        warning_codes = {
            "advisory-priority",
            "experimental-keywords",
            "unknown-extension-namespace",
            "unknown-unprefixed-field",
        }
        if not valid and all(code in warning_codes for code in diagnostics):
            diagnostics.append("schema-validation-failed")
        return valid, frontmatter, diagnostics

    if not frontmatter:
        return (
            True,
            {"spec-version": 1, "activation": "always"},
            ["legacy-implicit-always"],
        )

    trigger = frontmatter.get("trigger")
    keys = set(frontmatter)
    metadata_fields = {"name", "description", "tags"}

    if trigger is None:
        if keys <= metadata_fields:
            normalized = dict(frontmatter)
            normalized["spec-version"] = 1
            normalized["activation"] = "always"
            if not rule_validator.is_valid(normalized):
                return False, None, ["legacy-invalid-field"]
            return True, normalized, ["legacy-implicit-always"]
        if "globs" in keys or "applyTo" in keys:
            return False, None, ["legacy-unknown-condition-field"]
        if any(field.startswith("x-") for field in keys):
            return False, None, ["legacy-extension-without-trigger"]
        if "paths" in keys or "keywords" in keys:
            return False, None, ["legacy-condition-without-trigger"]
        return False, None, ["legacy-unknown-field-without-trigger"]

    if trigger == "always":
        if any(field not in LEGACY_FIELDS for field in keys):
            return False, None, ["legacy-unknown-field"]
        if "paths" in keys or "keywords" in keys:
            return False, None, ["legacy-always-with-condition"]
        normalized = {
            "spec-version": 1,
            **{field: value for field, value in frontmatter.items() if field != "trigger"},
            "activation": "always",
        }
        if not rule_validator.is_valid(normalized):
            return False, None, ["legacy-invalid-field"]
        return True, normalized, []

    if trigger == "auto":
        if any(field not in LEGACY_FIELDS for field in keys):
            return False, None, ["legacy-unknown-field"]
        has_paths = "paths" in keys
        has_keywords = "keywords" in keys
        if has_paths and has_keywords:
            return False, None, ["paths-keywords-combination-unresolved"]
        if not has_paths and not has_keywords:
            return False, None, ["legacy-auto-missing-condition"]
        normalized = {
            "spec-version": 1,
            **{field: value for field, value in frontmatter.items() if field != "trigger"},
            "activation": "on-match",
        }
        if not rule_validator.is_valid(normalized):
            return False, None, ["legacy-invalid-field"]
        return True, normalized, ["deprecated-auto"]

    if trigger == "manual":
        if any(field not in LEGACY_FIELDS for field in keys):
            return False, None, ["legacy-unknown-field"]
        if "keywords" in keys:
            return False, None, ["manual-keywords-invalid"]
        normalized = {
            "spec-version": 1,
            **{field: value for field, value in frontmatter.items() if field != "trigger"},
            "activation": "manual",
        }
        if not rule_validator.is_valid(normalized):
            return False, None, ["legacy-invalid-field"]
        return True, normalized, []

    return False, None, ["invalid-trigger"]


def compile_glob(pattern: str) -> re.Pattern[str]:
    result = ""
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            result += "(?:.*/)?"
            index += 3
        elif pattern.startswith("**", index):
            result += ".*"
            index += 2
        elif pattern[index] == "*":
            result += "[^/]*"
            index += 1
        elif pattern[index] == "?":
            result += "[^/]"
            index += 1
        else:
            result += re.escape(pattern[index])
            index += 1
    return re.compile(f"^{result}$")


def repository_root_diagnostic(repository_root: str) -> str | None:
    invalid = (
        not repository_root.startswith("/")
        or "\\" in repository_root
        or "//" in repository_root
        or (repository_root != "/" and repository_root.endswith("/"))
        or any(
            segment in {".", ".."}
            for segment in repository_root.split("/")
        )
    )
    return "invalid-repository-root" if invalid else None


def normalize_selector_path(
    repository_root: str, candidate: str
) -> tuple[str | None, str | None]:
    if repository_root_diagnostic(repository_root) is not None:
        return None, "invalid-repository-root"

    invalid = (
        not candidate
        or "\\" in candidate
        or "//" in candidate
        or candidate.endswith("/")
        or any(segment in {".", ".."} for segment in candidate.split("/"))
    )
    if invalid:
        return None, "invalid-selector-path"

    if candidate.startswith("/"):
        prefix = repository_root.rstrip("/") + "/"
        if not candidate.startswith(prefix):
            return None, "path-outside-repository"
        return candidate[len(prefix) :], None

    return candidate, None


def validate_examples(rule_validator: Draft202012Validator) -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "examples").glob("*.md")):
        try:
            frontmatter, _ = parse_rule_text(read_utf8(path))
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        if frontmatter is None:
            errors.append(f"{path.relative_to(ROOT)}: example must be versioned")
            continue

        for error in rule_validator.iter_errors(frontmatter):
            errors.append(
                f"{path.relative_to(ROOT)}: {error.json_path}: {error.message}"
            )

    return errors


def validate_parser_cases(
    rule_validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []
    corpus = load_yaml(ROOT / "conformance/v1/cases.yaml")
    normalized_cases: dict[str, dict[str, Any]] = {}

    for case in corpus["parser-cases"]:
        case_id = case["id"]
        expected = case["expected"]
        source_filename = case.get("source-filename")

        if source_filename is not None and not source_filename.endswith(".md"):
            actual_code = "invalid-rule-extension"
            expected_codes = {
                diagnostic["code"]
                for diagnostic in expected.get("diagnostics", [])
            }
            if expected["valid"] or expected_codes != {actual_code}:
                errors.append(
                    f"{case_id}: invalid extension expectation does not match"
                )
            continue

        try:
            if "document-file" in case:
                text = read_utf8(ROOT / "conformance/v1" / case["document-file"])
            elif "document-bytes" in case:
                text = decode_utf8(bytes.fromhex(case["document-bytes"]), case_id)
            else:
                text = case["document"]
            frontmatter, body = parse_rule_text(text)
        except (ValueError, yaml.YAMLError) as exc:
            if expected["valid"]:
                errors.append(f"{case_id}: unexpected parser failure: {exc}")
                continue
            message = str(exc)
            if "duplicate key" in message:
                actual_code = "duplicate-frontmatter-key"
            elif "unclosed frontmatter" in message:
                actual_code = "unclosed-frontmatter"
            elif "frontmatter must be a mapping" in message:
                actual_code = "frontmatter-not-mapping"
            elif "byte-order marks" in message:
                actual_code = "unsupported-byte-order-mark"
            elif "invalid UTF-8" in message:
                actual_code = "invalid-utf8"
            else:
                actual_code = "unsupported-yaml-feature"
            expected_codes = [
                diagnostic["code"]
                for diagnostic in expected.get("diagnostics", [])
            ]
            if {actual_code} != set(expected_codes):
                errors.append(
                    f"{case_id}: diagnostics {[actual_code]} != expected "
                    f"{expected_codes}"
                )
            continue

        actual_valid, normalized, diagnostics = normalize_rule(
            frontmatter, rule_validator
        )
        if (
            actual_valid
            and normalized is not None
            and "name" not in normalized
            and source_filename is not None
        ):
            effective_name = Path(source_filename).stem
            if len(effective_name) > 64 or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", effective_name
            ):
                diagnostics.append("invalid-effective-name")

        if actual_valid != expected["valid"]:
            errors.append(
                f"{case_id}: validity {actual_valid} != expected {expected['valid']}"
            )

        expected_profile = expected.get("profile")
        if expected_profile is not None:
            if frontmatter is None or "spec-version" not in frontmatter:
                actual_profile = "legacy"
            elif normalized is not None and (
                normalized.get("activation") == "manual"
                or "keywords" in normalized
                or "priority" in normalized
            ):
                actual_profile = "experimental"
            else:
                actual_profile = "core"
            if actual_profile != expected_profile:
                errors.append(
                    f"{case_id}: profile {actual_profile} != expected "
                    f"{expected_profile}"
                )

        expected_capabilities = set(expected.get("capabilities", []))
        if expected_capabilities and normalized is not None:
            actual_capabilities: set[str] = set()
            if normalized.get("activation") == "manual":
                actual_capabilities.add("manual")
                if "paths" in normalized:
                    actual_capabilities.add("manual-paths")
            for capability in ("keywords", "priority"):
                if capability in normalized:
                    actual_capabilities.add(capability)
            if actual_capabilities != expected_capabilities:
                errors.append(
                    f"{case_id}: capabilities {sorted(actual_capabilities)} "
                    f"!= expected {sorted(expected_capabilities)}"
                )

        for field, value in expected.get("preserved-fields", {}).items():
            preserved_source = normalized if normalized is not None else frontmatter
            if preserved_source is None or preserved_source.get(field) != value:
                errors.append(f"{case_id}: field {field} was not preserved")

        expected_exact = expected.get("exact-interpretation")
        if expected_exact is not None:
            if frontmatter is not None and any(
                field not in KNOWN_FIELDS and not field.startswith("x-")
                for field in frontmatter
            ):
                actual_exact: bool | str = False
            elif frontmatter is not None and any(
                field.startswith("x-") for field in frontmatter
            ):
                actual_exact = "namespace-dependent"
            else:
                actual_exact = True
            if actual_exact != expected_exact:
                errors.append(
                    f"{case_id}: exact interpretation {actual_exact} != "
                    f"expected {expected_exact}"
                )

        expected_diagnostics = [
            diagnostic["code"] for diagnostic in expected.get("diagnostics", [])
        ]
        if set(diagnostics) != set(expected_diagnostics):
            errors.append(
                f"{case_id}: diagnostics {diagnostics} != expected "
                f"{expected_diagnostics}"
            )

        expected_normalized = expected.get("normalized-frontmatter")
        if expected_normalized is not None and normalized != expected_normalized:
            errors.append(
                f"{case_id}: normalized {normalized} != expected "
                f"{expected_normalized}"
            )

        if actual_valid and normalized is not None:
            normalized_cases[case_id] = normalized

        if expected.get("body-preservation") == "byte-exact-after-closing-delimiter":
            delimiter = re.match(
                r"\A---\r?\n.*?^---\r?\n", text, re.DOTALL | re.MULTILINE
            )
            if delimiter is None or body != text[delimiter.end() :]:
                errors.append(
                    f"{case_id}: body was not preserved after closing delimiter"
                )

    for selector_case in corpus["selector-cases"]:
        case_id = selector_case["id"]
        rule_case = selector_case["rule-case"]
        if rule_case not in normalized_cases:
            errors.append(
                f"{case_id}: unknown or invalid rule-case {rule_case}"
            )
            continue

        rule = normalized_cases[rule_case]
        actual_diagnostics: list[str] = []
        normalized_paths: list[str] = []
        root_diagnostic = repository_root_diagnostic(
            selector_case["repository-root"]
        )
        if root_diagnostic is not None:
            actual_diagnostics.append(root_diagnostic)
        else:
            for candidate in selector_case["paths"]:
                normalized_path, diagnostic = normalize_selector_path(
                    selector_case["repository-root"], candidate
                )
                if diagnostic is not None:
                    actual_diagnostics.append(diagnostic)
                elif normalized_path is not None:
                    normalized_paths.append(normalized_path)

        if actual_diagnostics:
            selected = False
        elif rule["activation"] == "always":
            selected = True
        else:
            patterns = [compile_glob(pattern) for pattern in rule.get("paths", [])]
            selected = any(
                pattern.match(path)
                for pattern in patterns
                for path in normalized_paths
            )

        expected = selector_case["expected"]
        if selected != expected["selected"]:
            errors.append(
                f"{case_id}: selected {selected} != expected {expected['selected']}"
            )

        expected_diagnostics = [
            diagnostic["code"] for diagnostic in expected.get("diagnostics", [])
        ]
        if set(actual_diagnostics) != set(expected_diagnostics):
            errors.append(
                f"{case_id}: diagnostics {actual_diagnostics} != expected "
                f"{expected_diagnostics}"
            )

    return errors


def validate_projections(
    projection_validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []
    corpus = load_yaml(ROOT / "conformance/v1/projections.yaml")
    parser_corpus = load_yaml(ROOT / "conformance/v1/cases.yaml")
    profiles = corpus["profiles"]
    source_documents: dict[str, dict[str, Any]] = {}

    for case in parser_corpus["parser-cases"]:
        if "document" not in case:
            continue
        try:
            frontmatter, body = parse_rule_text(case["document"])
        except (ValueError, yaml.YAMLError):
            continue
        source_documents[case["id"]] = {
            "frontmatter": frontmatter,
            "body": body,
            "source-filename": case.get("source-filename"),
        }

    for projection in corpus["projections"]:
        verification = projection.get("verification")
        if verification not in {
            "verified-docs",
            "verified-docs-and-2.1.205",
            "pending-path-semantics",
        }:
            errors.append(
                f"{projection['id']}: invalid or missing verification status"
            )
        profile_ref = projection["target-profile"]
        if profile_ref not in profiles:
            errors.append(f"{projection['id']}: unknown target profile {profile_ref}")
            continue

        expected = projection["expected"]
        result = {
            **expected,
            "target-profile": profiles[profile_ref],
        }

        for error in projection_validator.iter_errors(result):
            errors.append(
                f"{projection['id']}: {error.json_path}: {error.message}"
            )

        output = expected.get("output")
        source = source_documents.get(projection["source-case"])
        if source is None:
            errors.append(
                f"{projection['id']}: unknown source case "
                f"{projection['source-case']}"
            )
            continue
        if source["source-filename"] is None:
            errors.append(
                f"{projection['id']}: source case lacks source-filename"
            )
        if output is not None:
            if output["body"] != source["body"]:
                errors.append(
                    f"{projection['id']}: output body differs from source body"
                )

        frontmatter = source["frontmatter"]
        capabilities = profiles[profile_ref]["capabilities"]
        unsupported_behavior = (
            frontmatter["activation"] not in capabilities["activation-modes"]
            or (
                frontmatter["activation"] != "manual"
                and "paths" in frontmatter
                and (
                    capabilities["path-semantics"] == "none"
                    or (
                        capabilities["path-semantics"] == "unverified"
                        and verification != "pending-path-semantics"
                    )
                )
            )
            or (
                "keywords" in frontmatter
                and not capabilities["keywords"]
            )
            or (
                "priority" in frontmatter
                and not capabilities["priority"]
            )
        )
        if expected["outcome"] == "exact" and unsupported_behavior:
            errors.append(
                f"{projection['id']}: exact outcome conflicts with target capabilities"
            )
        if expected["outcome"] in {"lossy", "unsupported"} and not unsupported_behavior:
            errors.append(
                f"{projection['id']}: non-exact outcome lacks a capability mismatch"
            )

    return errors


def validate_diagnostics() -> list[str]:
    errors: list[str] = []
    registry = load_yaml(ROOT / "conformance/v1/diagnostics.yaml")
    codes = registry["codes"]
    used_codes: set[str] = set()

    for code, severity in codes.items():
        if not isinstance(code, str) or not re.fullmatch(
            r"[a-z][a-z0-9-]*", code
        ):
            errors.append(f"invalid diagnostic code: {code!r}")
        if severity not in {"error", "warning", "info"}:
            errors.append(
                f"diagnostic {code}: invalid severity {severity!r}"
            )

    corpus = load_yaml(ROOT / "conformance/v1/cases.yaml")
    for group in ("parser-cases", "selector-cases"):
        for case in corpus[group]:
            for diagnostic in case["expected"].get("diagnostics", []):
                if set(diagnostic) != {"code"} or not isinstance(
                    diagnostic.get("code"), str
                ):
                    errors.append(
                        f"{case['id']}: diagnostic expectation must contain "
                        "one string code"
                    )
                    continue
                code = diagnostic["code"]
                used_codes.add(code)
                if code not in codes:
                    errors.append(
                        f"{case['id']}: unregistered diagnostic code {code}"
                    )

    for code in sorted(set(codes) - used_codes):
        errors.append(f"diagnostic {code}: no conformance case")

    return errors


def validate_spec_index() -> list[str]:
    errors: list[str] = []
    index = load_yaml(ROOT / "spec/index.yaml")

    paths: list[str] = [index["normative"]["rfc"]]
    paths.extend(index["normative"]["schemas"])
    paths.extend(index["normative"]["conformance"])
    paths.extend(index["informative"].values())

    for relative in paths:
        if not (ROOT / relative).exists():
            errors.append(f"spec/index.yaml references missing path: {relative}")

    return errors


def main() -> int:
    rule_validator = load_schema(ROOT / "schema/agent-rule.schema.json")
    projection_validator = load_schema(
        ROOT / "schema/projection-result.schema.json"
    )

    errors = [
        *validate_examples(rule_validator),
        *validate_parser_cases(rule_validator),
        *validate_projections(projection_validator),
        *validate_diagnostics(),
        *validate_spec_index(),
    ]

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Checked schemas, examples, conformance fixtures, and spec index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
