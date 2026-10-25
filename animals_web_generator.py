"""Generate an animal-card HTML page from the supplied JSON data."""

import json
from html import escape
from pathlib import Path
from typing import Any


PROJECT_DIRECTORY = Path(__file__).parent
DATA_FILE = PROJECT_DIRECTORY / "animals_data.json"
TEMPLATE_FILE = PROJECT_DIRECTORY / "animals_template.html"
OUTPUT_FILE = PROJECT_DIRECTORY / "animals.html"
TEMPLATE_MARKER = "__REPLACE_ANIMALS_INFO__"


def load_data(file_path: Path | str) -> list[dict[str, Any]]:
    """Load and return the animal records from a JSON file."""
    with Path(file_path).open(encoding="utf-8") as handle:
        return json.load(handle)


def serialize_animal(animal: dict[str, Any]) -> str:
    """Convert one animal record into the guide's required card markup."""
    name = escape(str(animal["name"]))
    diet = escape(str(animal["characteristics"]["diet"]))
    locations = " and ".join(map(str, animal["locations"]))
    animal_class = escape(str(animal["taxonomy"]["class"]))

    return (
        '    <li class="cards__item">\n'
        f'        <div class="card__title">{name}</div>\n'
        '        <p class="card__text">\n'
        f'            <strong>Diet:</strong> {diet}<br/>\n'
        f'            <strong>Location:</strong> {escape(locations)}<br/>\n'
        f'            <strong>Type:</strong> {animal_class}<br/>\n'
        '        </p>\n'
        '    </li>'
    )


def generate_html(
    data_file: Path | str = DATA_FILE,
    template_file: Path | str = TEMPLATE_FILE,
    output_file: Path | str = OUTPUT_FILE,
) -> Path:
    """Fill the supplied HTML template with an HTML card for every animal."""
    animals = load_data(data_file)
    template = Path(template_file).read_text(encoding="utf-8")
    animal_cards = "\n".join(serialize_animal(animal) for animal in animals)

    if TEMPLATE_MARKER not in template:
        raise ValueError(f"Template marker {TEMPLATE_MARKER!r} was not found.")

    output_path = Path(output_file)
    output_path.write_text(
        template.replace(TEMPLATE_MARKER, animal_cards), encoding="utf-8"
    )
    return output_path


def main() -> None:
    """Generate animals.html and report its path."""
    output_path = generate_html()
    animal_count = len(load_data(DATA_FILE))
    print(f"Generated {output_path.name} with {animal_count} animal cards.")


if __name__ == "__main__":
    main()
