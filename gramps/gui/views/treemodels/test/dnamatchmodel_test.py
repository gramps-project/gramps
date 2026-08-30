#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Unittests for the DNA match list view columns."""

# ------------------------
# Python modules
# ------------------------
import unittest

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.lib import DNAMatch, PredictedRelationship
from gramps.gen.lib.json_utils import object_to_data
from gramps.gui.views.treemodels.dnamatchmodel import DNAMatchModel


class _Model(DNAMatchModel):
    """DNAMatchModel with the database-backed initialisation skipped."""

    def __init__(self):
        pass


def _prediction(description="", subject_gens=0, match_gens=0, probability=0.0):
    """Return a PredictedRelationship carrying the given values."""
    rel = PredictedRelationship()
    rel.set_description(description)
    rel.set_subject_mrca_gens(subject_gens)
    rel.set_match_mrca_gens(match_gens)
    rel.set_probability(probability)
    return rel


def _column(*predictions):
    """Return the predicted relationship column for a match holding predictions."""
    match = DNAMatch()
    for rel in predictions:
        match.add_predicted_relationship(rel)
    return _Model().column_predicted_rel(object_to_data(match))


class TestPredictedRelationshipColumn(unittest.TestCase):
    """A prediction with no description falls back to its generation counts."""

    def test_description_is_used_when_present(self):
        self.assertEqual(
            _column(_prediction(description="Second cousins")), "Second cousins"
        )

    def test_equal_generations_without_description(self):
        self.assertEqual(
            _column(_prediction(subject_gens=4, match_gens=4)), "4 generations"
        )

    def test_one_generation_is_singular(self):
        self.assertEqual(
            _column(_prediction(subject_gens=1, match_gens=1)), "1 generation"
        )

    def test_differing_generations_show_both_sides(self):
        self.assertEqual(
            _column(_prediction(subject_gens=3, match_gens=4)), "3 / 4 generations"
        )

    def test_generations_on_one_side_only(self):
        self.assertEqual(_column(_prediction(subject_gens=3)), "3 generations")
        self.assertEqual(_column(_prediction(match_gens=3)), "3 generations")

    def test_description_wins_over_generations(self):
        self.assertEqual(
            _column(_prediction(description="Half second cousins", subject_gens=3)),
            "Half second cousins",
        )

    def test_probability_alone_carries_no_placeholder(self):
        self.assertEqual(_column(_prediction(probability=62)), "(62%)")

    def test_generations_and_probability(self):
        self.assertEqual(
            _column(_prediction(subject_gens=4, match_gens=4, probability=62)),
            "4 generations (62%)",
        )

    def test_empty_prediction_renders_blank(self):
        self.assertEqual(_column(_prediction()), "")

    def test_no_predictions_render_blank(self):
        self.assertEqual(_column(), "")

    def test_alternative_count_is_appended(self):
        self.assertEqual(
            _column(
                _prediction(subject_gens=4, match_gens=4, probability=62),
                _prediction(description="Third cousins", probability=20),
            ),
            "4 generations (62%) (+1)",
        )

    def test_alternative_count_without_a_label(self):
        self.assertEqual(
            _column(_prediction(), _prediction(description="Third cousins")),
            "(+1)",
        )


if __name__ == "__main__":
    unittest.main()
