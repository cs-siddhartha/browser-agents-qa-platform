from collections.abc import Iterable
from pathlib import Path

import yaml
from pydantic import ValidationError
from yaml.nodes import MappingNode

from browser_agents_qa.skills.models import SkillDefinition

PACKAGE_ROOT = Path(__file__).parent.parent
DEFAULT_CATALOGUE_PATH = PACKAGE_ROOT / "config" / "skills.yaml"


class UniqueKeyLoader(yaml.SafeLoader):
    """Load YAML mappings while rejecting duplicate keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    """Construct one YAML mapping and reject repeated keys."""

    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class SkillCatalogueError(ValueError):
    """Identify an invalid or inconsistent skill catalogue."""


class SkillCatalogue:
    """Store validated YAML skill definitions by unique skill name."""

    def __init__(self, skills: Iterable[SkillDefinition]) -> None:
        """Build a catalogue and reject duplicate or unknown fallback skills."""

        self._skills: dict[str, SkillDefinition] = {}
        for skill in skills:
            if skill.name in self._skills:
                raise SkillCatalogueError(f"Duplicate skill name: {skill.name}")
            self._skills[skill.name] = skill

        for skill in self._skills.values():
            unknown_fallbacks = set(skill.fallbacks) - self._skills.keys()
            if unknown_fallbacks:
                unknown = ", ".join(sorted(unknown_fallbacks))
                raise SkillCatalogueError(
                    f"Skill '{skill.name}' has unknown fallbacks: {unknown}"
                )

    @classmethod
    def from_yaml(cls, path: Path) -> "SkillCatalogue":
        """Load central YAML metadata and referenced Markdown prompts."""

        if not path.is_file():
            raise SkillCatalogueError(f"Skill catalogue not found: {path}")

        try:
            raw_catalogue = yaml.load(
                path.read_text(encoding="utf-8"),
                Loader=UniqueKeyLoader,
            )
        except yaml.YAMLError as error:
            raise SkillCatalogueError(f"Invalid skill catalogue YAML in {path}: {error}") from error

        if not isinstance(raw_catalogue, dict) or not raw_catalogue:
            raise SkillCatalogueError(f"Skill catalogue must be a non-empty mapping: {path}")

        package_root = path.parent.parent
        skills = (
            _load_skill_definition(name, config, package_root, path)
            for name, config in raw_catalogue.items()
        )
        return cls(skills)

    def get(self, name: str) -> SkillDefinition:
        """Return one skill or fail when a planner selects an unknown name."""

        try:
            return self._skills[name]
        except KeyError as error:
            raise SkillCatalogueError(f"Unknown skill: {name}") from error

    def list(self) -> tuple[SkillDefinition, ...]:
        """Return all skills in deterministic name order for planner prompts."""

        return tuple(self._skills[name] for name in sorted(self._skills))

    def planner_context(self) -> str:
        """Render concise capability metadata for an LLM planner prompt."""

        return "\n".join(
            (
                f"- {skill.name}: {skill.description} "
                f"(layer={skill.layer}, inputs={','.join(skill.inputs) or 'none'}, "
                f"fallbacks={','.join(skill.fallbacks) or 'none'})"
            )
            for skill in self.list()
        )


def _load_skill_definition(
    name: object,
    config: object,
    package_root: Path,
    catalogue_path: Path,
) -> SkillDefinition:
    """Load and validate one configured skill and its Markdown instructions."""

    if not isinstance(name, str) or not isinstance(config, dict):
        raise SkillCatalogueError(
            f"Every skill in {catalogue_path} must map a string name to an object."
        )

    prompt_value = config.get("prompt")
    if not isinstance(prompt_value, str) or not prompt_value:
        raise SkillCatalogueError(f"Skill '{name}' must declare a prompt path.")

    prompt_path = (package_root / prompt_value).resolve()
    resolved_root = package_root.resolve()
    if not prompt_path.is_relative_to(resolved_root):
        raise SkillCatalogueError(f"Skill '{name}' prompt escapes the package root.")
    if not prompt_path.is_file():
        raise SkillCatalogueError(f"Skill '{name}' prompt not found: {prompt_path}")

    try:
        return SkillDefinition.model_validate(
            {
                "name": name,
                **config,
                "instructions": prompt_path.read_text(encoding="utf-8").strip(),
            }
        )
    except ValidationError as error:
        raise SkillCatalogueError(
            f"Invalid skill '{name}' in {catalogue_path}: {error}"
        ) from error


def load_default_catalogue() -> SkillCatalogue:
    """Load the skill catalogue distributed with the application package."""

    return SkillCatalogue.from_yaml(DEFAULT_CATALOGUE_PATH)
