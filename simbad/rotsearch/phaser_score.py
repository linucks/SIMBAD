"""Class to store PHASER rotation scores"""

__author__ = "Adam Simpkin"
__date__ = "27 Dec 2017"
__version__ = "0.1"


class PhaserRotationScore(object):
    """An phaser rotation scoring class"""

    __slots__ = ("pdb_code", "dat_path", "LLG", "RFZ")

    def __init__(self, pdb_code, dat_path, LLG, RFZ):
        self.pdb_code = pdb_code
        self.dat_path = dat_path
        self.LLG = LLG
        self.RFZ = RFZ

    def __repr__(self):
        string = "{name}(pdb_code={pdb_code} dat_path={dat_path} LLG={LLG} RFZ={RFZ})"
        return string.format(name=self.__class__.__name__, **{k: getattr(self, k) for k in self.__slots__})

    def _as_dict(self):
        """Convert the :obj:`PhaserRotationScore <simbad.rotsearch.phaser_score.PhaserRotationScore>`
        object to a dictionary"""
        return {k: getattr(self, k) for k in self.__slots__}