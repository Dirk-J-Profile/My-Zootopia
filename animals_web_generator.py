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


def available_skin_types(animals: list[dict[str, Any]]) -> list[str]:
    """Return the distinct skin types supplied by the animal records."""
    skin_types = {
        str(animal["characteristics"]["skin_type"])
        for animal in animals
        if animal["characteristics"].get("skin_type")
    }
    return sorted(skin_types)


def filter_by_skin_type(
    animals: list[dict[str, Any]], selected_skin_type: str
) -> list[dict[str, Any]]:
    """Return animals matching the selection without case sensitivity."""
    normalized_skin_type = selected_skin_type.strip().casefold()
    return [
        animal
        for animal in animals
        if str(animal["characteristics"].get("skin_type", "")).casefold()
        == normalized_skin_type
    ]


def serialize_animal(animal: dict[str, Any]) -> str:
    """Convert one animal record into the guide's required card markup."""
    name = escape(str(animal["name"]))
    diet = escape(str(animal["characteristics"]["diet"]))
    locations = " and ".join(map(str, animal["locations"]))
    animal_type = animal["characteristics"].get("type")
    skin_type = animal["characteristics"].get("skin_type")
    type_line = ""
    if animal_type:
        escaped_type = escape(str(animal_type))
        type_line = (
            "            <li><strong>Type:</strong> "
            f"{escaped_type}</li>\n"
        )
    skin_type_line = ""
    if skin_type:
        escaped_skin_type = escape(str(skin_type))
        skin_type_line = (
            "            <li><strong>Skin Type:</strong> "
            f"{escaped_skin_type}</li>\n"
        )

    return (
        '    <li class="cards__item">\n'
        f'        <div class="card__title">{name}</div>\n'
        '        <div class="card__text">\n'
        '            <ul>\n'
        f'            <li><strong>Diet:</strong> {diet}</li>\n'
        "            <li><strong>Location:</strong> "
        f"{escape(locations)}</li>\n"
        f'{type_line}'
        f'{skin_type_line}'
        '            </ul>\n'
        '        </div>\n'
        '    </li>'
    )


def generate_html(
    data_file: Path | str = DATA_FILE,
    template_file: Path | str = TEMPLATE_FILE,
    output_file: Path | str = OUTPUT_FILE,
    animals: list[dict[str, Any]] | None = None,
) -> Path:
    """Fill the supplied HTML template with an HTML card for every animal."""
    if animals is None:
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
    """Generate a page for the skin type chosen by the user."""
    animals = load_data(DATA_FILE)
    skin_types = available_skin_types(animals)
    print(f"Available skin types: {', '.join(skin_types)}")
    selected_skin_type = input("Select a skin type: ")
    filtered_animals = filter_by_skin_type(animals, selected_skin_type)
    if not filtered_animals:
        print(f"No animals found with skin type: {selected_skin_type}")
        return

    output_path = generate_html(animals=filtered_animals)
    animal_count = len(filtered_animals)
    print(f"Generated {output_path.name} with {animal_count} animal cards.")


if __name__ == "__main__":
    main()
