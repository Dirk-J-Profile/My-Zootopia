"""Behavioral tests for the Zootopia HTML generator."""

import tempfile
import unittest
from pathlib import Path
from subprocess import run
import sys

from animals_web_generator import (
    available_skin_types,
    filter_by_skin_type,
    generate_html,
    load_data,
    serialize_animal,
)


PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "animals_data.json"
TEMPLATE_FILE = PROJECT_DIR / "animals_template.html"


class ZootopiaGeneratorTests(unittest.TestCase):
    """Verify data loading, card serialization, and full page generation."""

    def test_load_data_reads_all_animals(self):
        """The supplied JSON file is read as its 19 animal records."""
        animals = load_data(DATA_FILE)
        self.assertEqual(19, len(animals))
        self.assertEqual("American Foxhound", animals[0]["name"])

    def test_available_skin_types_are_unique_and_sorted(self):
        """Available skin types come from the JSON data without duplicates."""
        animals = [
            {"characteristics": {"skin_type": "Hair"}},
            {"characteristics": {"skin_type": "Fur"}},
            {"characteristics": {"skin_type": "Hair"}},
        ]

        self.assertEqual(["Fur", "Hair"], available_skin_types(animals))

    def test_filter_by_skin_type_matches_without_case_sensitivity(self):
        """A selected skin type retains only matching animal records."""
        animals = [
            {"name": "Hair animal", "characteristics": {"skin_type": "Hair"}},
            {"name": "Fur animal", "characteristics": {"skin_type": "Fur"}},
        ]

        filtered_animals = filter_by_skin_type(animals, "hair")

        filtered_names = [animal["name"] for animal in filtered_animals]
        self.assertEqual(["Hair animal"], filtered_names)

    def test_filter_by_skin_type_returns_no_animals_for_unknown_value(self):
        """An unsupported selection is handled as an empty result."""
        animals = [
            {"name": "Hair animal", "characteristics": {"skin_type": "Hair"}}
        ]

        self.assertEqual([], filter_by_skin_type(animals, "Scales"))

    def test_serialize_animal_builds_a_card_with_required_details(self):
        """One data record becomes the guide's required HTML card structure."""
        animal = {
            "name": "Wire Fox Terrier",
            "characteristics": {
                "diet": "Carnivore",
                "type": "mammal",
                "skin_type": "Fur",
            },
            "locations": ["North-America", "Canada"],
            "taxonomy": {"class": "Reptilia"},
        }
        card = serialize_animal(animal)
        self.assertIn('<li class="cards__item">', card)
        self.assertIn('<div class="card__title">Wire Fox Terrier</div>', card)
        self.assertIn('<div class="card__text">', card)
        self.assertIn("<ul>", card)
        self.assertIn("<li><strong>Diet:</strong> Carnivore</li>", card)
        self.assertIn(
            "<li><strong>Location:</strong> North-America and Canada</li>",
            card,
        )
        self.assertIn("<li><strong>Type:</strong> mammal</li>", card)
        self.assertIn("<li><strong>Skin Type:</strong> Fur</li>", card)
        self.assertNotIn("<br/>", card)
        self.assertNotIn("Reptilia", card)
        self.assertTrue(card.rstrip().endswith("</li>"))

    def test_serialize_animal_omits_missing_optional_type(self):
        """Records without characteristics.type remain serializable."""
        animal = {
            "name": "English Foxhound",
            "characteristics": {"diet": "Omnivore"},
            "locations": ["Europe"],
            "taxonomy": {"class": "Mammalia"},
        }

        card = serialize_animal(animal)

        self.assertIn("<li><strong>Location:</strong> Europe</li>", card)
        self.assertNotIn("<strong>Type:</strong>", card)

    def test_serialize_animal_escapes_html_values(self):
        """Animal values cannot inject markup into the generated card."""
        animal = {
            "name": "Fox <&>",
            "characteristics": {"diet": "Fish & Chips"},
            "locations": ["North <America>"],
        }

        card = serialize_animal(animal)

        self.assertIn("Fox &lt;&amp;&gt;", card)
        self.assertIn("Fish &amp; Chips", card)
        self.assertIn("North &lt;America&gt;", card)
        self.assertNotIn("<strong>Type:</strong>", card)
        self.assertNotIn("<strong>Skin Type:</strong>", card)

    def test_generate_html_replaces_template_marker_with_all_cards(self):
        """The page has 19 cards and no unreplaced template marker."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_file = Path(temporary_directory) / "animals.html"
            generate_html(DATA_FILE, TEMPLATE_FILE, output_file)
            generated_html = output_file.read_text(encoding="utf-8")

        self.assertNotIn("__REPLACE_ANIMALS_INFO__", generated_html)
        self.assertEqual(19, generated_html.count('<li class="cards__item">'))
        self.assertIn("My Animal Repository", generated_html)
        self.assertIn("Wire Fox Terrier", generated_html)

    def test_pycharm_entry_point_runs_the_filtered_generator(self):
        """Running main.py lists types and generates cards for Hair only."""
        result = run(
            [sys.executable, "main.py"],
            check=True,
            capture_output=True,
            input="Hair\n",
            text=True,
            cwd=PROJECT_DIR,
        )
        expected_message = "Generated animals.html with 8 animal cards."
        self.assertIn("Available skin types:", result.stdout)
        self.assertIn(expected_message, result.stdout)
        generated_html = (PROJECT_DIR / "animals.html").read_text(
            encoding="utf-8"
        )
        self.assertEqual(8, generated_html.count('<li class="cards__item">'))
        self.assertNotIn("Arctic Fox", generated_html)


if __name__ == "__main__":
    unittest.main()
