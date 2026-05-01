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

"""
DNASegment secondary object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .secondaryobj import SecondaryObject

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# DNASegment
#
# -------------------------------------------------------------------------
class DNASegment(SecondaryObject):
    """
    A single shared DNA segment within a DNAMatch.

    Coordinates are in base pairs in the reference assembly recorded on
    the subject DNATest (DNAMatch.subject_test_handle.genome_build).
    """

    PHASE_UNASSIGNED = 0
    PHASE_UNKNOWN = 1
    PHASE_MATERNAL = 2
    PHASE_PATERNAL = 3

    def __init__(self, source=None):
        """
        Create a new DNASegment instance, copying from source if present.

        :param source: A DNASegment used to initialize the new instance.
        :type source: DNASegment
        """
        if source:
            self.__chromosome = source.__chromosome
            self.__start_bp = source.__start_bp
            self.__end_bp = source.__end_bp
            self.__start_rsid = source.__start_rsid
            self.__end_rsid = source.__end_rsid
            self.__shared_cm = source.__shared_cm
            self.__snp_count = source.__snp_count
            self.__phase = source.__phase
        else:
            self.__chromosome = ""
            self.__start_bp = 0
            self.__end_bp = 0
            self.__start_rsid = None
            self.__end_rsid = None
            self.__shared_cm = 0.0
            self.__snp_count = 0
            self.__phase = DNASegment.PHASE_UNASSIGNED

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.__chromosome,
            self.__start_bp,
            self.__end_bp,
            self.__start_rsid,
            self.__end_rsid,
            self.__shared_cm,
            self.__snp_count,
            self.__phase,
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (
            self.__chromosome,
            self.__start_bp,
            self.__end_bp,
            self.__start_rsid,
            self.__end_rsid,
            self.__shared_cm,
            self.__snp_count,
            self.__phase,
        ) = data
        return self

    def get_object_state(self):
        """
        Get the current object state as a dictionary.
        """
        attr_dict = super().get_object_state()
        attr_dict["chromosome"] = self.__chromosome
        attr_dict["start_bp"] = self.__start_bp
        attr_dict["end_bp"] = self.__end_bp
        attr_dict["start_rsid"] = self.__start_rsid
        attr_dict["end_rsid"] = self.__end_rsid
        attr_dict["shared_cm"] = self.__shared_cm
        attr_dict["snp_count"] = self.__snp_count
        attr_dict["phase"] = self.__phase
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using the provided dictionary.
        """
        self.__chromosome = attr_dict.pop("chromosome")
        self.__start_bp = attr_dict.pop("start_bp")
        self.__end_bp = attr_dict.pop("end_bp")
        self.__start_rsid = attr_dict.pop("start_rsid")
        self.__end_rsid = attr_dict.pop("end_rsid")
        self.__shared_cm = attr_dict.pop("shared_cm")
        self.__snp_count = attr_dict.pop("snp_count")
        self.__phase = attr_dict.pop("phase")
        super().set_object_state(attr_dict)

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.
        """
        return {
            "type": "object",
            "title": _("DNA Segment"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "chromosome": {"type": "string", "title": _("Chromosome")},
                "start_bp": {"type": "integer", "title": _("Start position")},
                "end_bp": {"type": "integer", "title": _("End position")},
                "start_rsid": {
                    "type": ["string", "null"],
                    "title": _("Start RSID"),
                },
                "end_rsid": {
                    "type": ["string", "null"],
                    "title": _("End RSID"),
                },
                "shared_cm": {"type": "number", "title": _("Shared cM")},
                "snp_count": {"type": "integer", "title": _("SNP count")},
                "phase": {"type": "integer", "title": _("Phase")},
            },
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.
        """
        return [self.__chromosome]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        """
        return []

    def get_handle_referents(self):
        """
        Return the list of child objects which may reference primary objects.
        """
        return []

    def set_chromosome(self, chromosome):
        """Set the chromosome identifier."""
        self.__chromosome = chromosome

    def get_chromosome(self):
        """Return the chromosome identifier."""
        return self.__chromosome

    chromosome = property(get_chromosome, set_chromosome)

    def set_start_bp(self, start_bp):
        """Set the start position in base pairs."""
        self.__start_bp = start_bp

    def get_start_bp(self):
        """Return the start position in base pairs."""
        return self.__start_bp

    start_bp = property(get_start_bp, set_start_bp)

    def set_end_bp(self, end_bp):
        """Set the end position in base pairs."""
        self.__end_bp = end_bp

    def get_end_bp(self):
        """Return the end position in base pairs."""
        return self.__end_bp

    end_bp = property(get_end_bp, set_end_bp)

    def set_start_rsid(self, rsid):
        """Set the RSID of the first SNP in the segment."""
        self.__start_rsid = rsid

    def get_start_rsid(self):
        """Return the RSID of the first SNP in the segment, or None."""
        return self.__start_rsid

    start_rsid = property(get_start_rsid, set_start_rsid)

    def set_end_rsid(self, rsid):
        """Set the RSID of the last SNP in the segment."""
        self.__end_rsid = rsid

    def get_end_rsid(self):
        """Return the RSID of the last SNP in the segment, or None."""
        return self.__end_rsid

    end_rsid = property(get_end_rsid, set_end_rsid)

    def set_shared_cm(self, cm):
        """Set the shared cM for this segment."""
        self.__shared_cm = cm

    def get_shared_cm(self):
        """Return the shared cM for this segment."""
        return self.__shared_cm

    shared_cm = property(get_shared_cm, set_shared_cm)

    def set_snp_count(self, count):
        """Set the number of SNPs compared in this segment."""
        self.__snp_count = count

    def get_snp_count(self):
        """Return the number of SNPs compared in this segment."""
        return self.__snp_count

    snp_count = property(get_snp_count, set_snp_count)

    def set_phase(self, phase):
        """Set the phase assignment for this segment."""
        self.__phase = phase

    def get_phase(self):
        """Return the phase assignment for this segment."""
        return self.__phase

    phase = property(get_phase, set_phase)
