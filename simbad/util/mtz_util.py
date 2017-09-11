"""Module for MTZ file I/O and manipulation"""

__author__ = "Adam Simpkin & Jens Thomas"
__date__ = "17 May 2017"
__version__ = "0.2"

from iotbx import reflection_file_reader
from iotbx.reflection_file_utils import looks_like_r_free_flags_info

import logging

logger = logging.getLogger(__name__)


class CreateMtz(object):
    """Class to create a temporary mtz containing all the columns needed for SIMBAD from input reflection file

    Attributes
    ----------
    input_reflection_file : str
        Path to the input reflection file in ccp4 mtz format
    output_mtz_file : str
        Path to the output mtz file

    Example
    -------
    >>> from simbad.util import mtz_util
    >>> CM = mtz_util.CreateMtz("<input_reflection_file>")
    >>> CM.output_mtz("<output_mtz_file>")
    """

    def __init__(self, input_reflection_file):

        self.amplitude_array = None
        self.anomalous_amplitude_array = None
        self.reconstructed_amplitude_array = None
        self.intensity_array = None
        self.anomalous_intensity_array = None
        self.free_array = None
        self.mtz_dataset = None

        reflection_file = reflection_file_reader.any_reflection_file(file_name=input_reflection_file)
        if not reflection_file.file_type() == "ccp4_mtz":
            msg = "File is not of type ccp4_mtz: {0}".format(input_reflection_file)
            logging.critical(msg)
            raise RuntimeError(msg)

        all_miller_arrays = reflection_file.as_miller_arrays()
        self.get_array_types(all_miller_arrays)
        self.process_miller_arrays()

    def add_array_to_mtz_dataset(self, miller_array, column_root_label):
        """Function to add cctbx miller array obj to cctbx mtz dataset obj

        Parameters
        ----------
        miller_array : cctbx :obj:
            Input cctbx obj containing a miller array
        column_root_label : str
            The root for the label of the output column

        Returns
        -------
        self.mtz_dataset : cctbx :obj:
            cctbx mtz obj containing the input miller array
        """
        if self.mtz_dataset:
            self.mtz_dataset.add_miller_array(miller_array, column_root_label=column_root_label)
        else:
            self.mtz_dataset = miller_array.as_mtz_dataset(column_root_label=column_root_label)
        return

    def create_amplitude_array(self, intensity_array):
        """Function to create a cctbx amplitude array from an cctbx intensity array

        Parameters
        ----------
        intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of intensities

        Returns
        -------
        self.amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of amplitudes
        """
        self.amplitude_array = intensity_array.set_observation_type_xray_amplitude()
        return

    def create_anomalous_amplitude_array(self, anomalous_intensity_array):
        """Function to create a cctbx anomalous amplitude array from a cctbx anomalous intensity array

        Parameters
        ----------
        anomalous_intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous intensities

        Returns
        -------
        self.anomalous_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous amplitudes
        """
        self.anomalous_amplitude_array = anomalous_intensity_array.set_observation_type_xray_amplitude()
        return

    def create_anomalous_intensity_array(self, anomalous_amplitude_array):
        """Function to create a cctbx anomalous intensity array from a cctbx anomalous amplitude array

        Parameters
        ----------
        anomalous_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous amplitudes

        Returns
        -------
        self.anomalous_intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous intensities
        """
        self.anomalous_intensity_array = anomalous_amplitude_array.set_observation_type_xray_intensity()
        return

    def create_intensity_array(self, amplitude_array):
        """Function to create a cctbx intensity array from a cctbx amplitude array

        Parameters
        ----------
        amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of amplitudes

        Returns
        -------
        self.intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of intensities
        """
        self.intensity_array = amplitude_array.set_observation_type_xray_intensity()
        return

    def create_merged_intensity_array(self, anomalous_intensity_array):
        """Function to create a cctbs intensity array from a cctbx anomalous intensity array

        Parameters
        ----------
        anomalous_intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous intensities

        Returns
        -------
        self.intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of intensities
        """
        merged_intensity_array = anomalous_intensity_array.as_non_anomalous_array().merge_equivalents()
        self.intensity_array = merged_intensity_array.array().set_observation_type_xray_intensity()
        return

    def create_reconstructed_amplitude_array(self, anomalous_amplitude_array):
        """Function to create a cctbx reconstructed amplitude array from a cctbx anomalous amplitude array

        Parameters
        ----------
        anomalous_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous amplitudes

        Returns
        -------
        self.reconstructed_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of reconstructed amplitudes
        """
        from cctbx.xray import observation_types
        self.reconstructed_amplitude_array = anomalous_amplitude_array.set_observation_type(
            observation_types.reconstructed_amplitude())
        return

    def get_array_types(self, all_miller_arrays):
        """Function to check array types contained within cctbx obj

        Parameters
        ----------
        all_miller_arrays : list
            A list of cctbx objects containing all miller arrays in a reflection file

        Returns
        -------
        self.free_array : cctbx :obj:
            A cctbx :obj: containing a miller array containing the Free R data
        self.amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of amplitudes
        self.anomalous_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous amplitudes
        self.reconstructed_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of reconstructed amplitudes
        self.intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of intensities
        self.anomalous_intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous intensities
        """
        for miller_array in all_miller_arrays:
            if miller_array.observation_type() is None:
                if looks_like_r_free_flags_info(miller_array.info()):
                    self.free_array = miller_array

            if miller_array.is_xray_amplitude_array and not miller_array.anomalous_flag():
                self.amplitude_array = miller_array
            elif miller_array.is_xray_amplitude_array and miller_array.anomalous_flag():
                self.anomalous_amplitude_array = miller_array
            elif miller_array.is_xray_reconstructed_amplitude_array:
                self.reconstructed_amplitude_array = miller_array
            elif miller_array.is_xray_intensity_array and not miller_array.anomalous_flag():
                self.intensity_array = miller_array
            elif miller_array.is_xray_intensity_array and miller_array.anomalous_flag():
                self.anomalous_intensity_array = miller_array
        return

    def output_mtz(self, output_mtz_file):
        """Function to output an mtz file from processed miller arrays

        Parameters
        ----------
        output_mtz_file : str
            Path to output mtz file

        Returns
        -------
        file
            mtz file containing all the columns needed to run SIMBAD
        """
        mtz_object = self.mtz_dataset.mtz_object()
        mtz_object.write(file_name=output_mtz_file)
        return

    def process_miller_arrays(self):
        """Function to process the miller arrays needed for SIMBAD

        Parameters
        ----------
        self.free_array : cctbx :obj:
            A cctbx :obj: containing a miller array containing the Free R data
        self.amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of amplitudes
        self.anomalous_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous amplitudes
        self.reconstructed_amplitude_array : cctbx :obj:
            A cctbx :obj: containing a miller array of reconstructed amplitudes
        self.intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of intensities
        self.anomalous_intensity_array : cctbx :obj:
            A cctbx :obj: containing a miller array of anomalous intensities

        Returns
        -------
        self.mtz_dataset : cctbx :obj:
            cctbx mtz obj containing all the miller arrays needed to run SIMBAD
        """

        # Add amplitudes
        if self.reconstructed_amplitude_array:
            self.add_array_to_mtz_dataset(self.reconstructed_amplitude_array, "F")
        elif self.anomalous_amplitude_array:
            self.create_reconstructed_amplitude_array(self.anomalous_amplitude_array)
            self.add_array_to_mtz_dataset(self.reconstructed_amplitude_array, "F")
        elif self.anomalous_intensity_array:
            self.create_anomalous_amplitude_array(self.anomalous_intensity_array)
            self.create_reconstructed_amplitude_array(self.anomalous_amplitude_array)
            self.add_array_to_mtz_dataset(self.reconstructed_amplitude_array, "F")
        elif self.amplitude_array:
            self.add_array_to_mtz_dataset(self.amplitude_array, "F")
        elif self.intensity_array:
            self.create_amplitude_array(self.intensity_array)
            self.add_array_to_mtz_dataset(self.amplitude_array, "F")
        else:
            msg = "No amplitudes of intensities found in input reflection file"
            logging.critical(msg)
            raise RuntimeError(msg)

        # Add intensities
        if self.intensity_array:
            self.add_array_to_mtz_dataset(self.intensity_array, "I")
        elif self.amplitude_array:
            self.create_intensity_array(self.amplitude_array)
            self.add_array_to_mtz_dataset(self.intensity_array, "I")
        elif self.anomalous_intensity_array:
            self.create_merged_intensity_array(self.anomalous_intensity_array)
            self.add_array_to_mtz_dataset(self.intensity_array, "I")
        elif self.anomalous_amplitude_array:
            self.create_anomalous_intensity_array(self.anomalous_amplitude_array)
            self.create_merged_intensity_array(self.anomalous_intensity_array)
            self.add_array_to_mtz_dataset(self.intensity_array, "I")
        elif self.reconstructed_amplitude_array:
            self.create_anomalous_intensity_array(self.reconstructed_amplitude_array)
            self.create_merged_intensity_array(self.anomalous_intensity_array)
            self.add_array_to_mtz_dataset(self.intensity_array, "I")
        else:
            msg = "No amplitudes of intensities found in input reflection file"
            logging.critical(msg)
            raise RuntimeError(msg)

        # Add free flag
        if self.free_array:
            column_root_label = self.free_array.info().labels[0]
            self.add_array_to_mtz_dataset(self.free_array, column_root_label)
        else:
            self.free_array = self.intensity_array.generate_r_free_flags(format='ccp4')
            self.add_array_to_mtz_dataset(self.free_array, "FreeR_flag")
        return


def crystal_data(mtz_file):
    """Set crystallographic parameters from mtz file

    Parameters
    ----------
    mtz_file : str
       The path to the mtz file

    Returns
    -------
    space_group : str
       The space group
    resolution : str
       The resolution
    cell_parameters : tuple
       The cell parameters

    """

    reflection_file = reflection_file_reader.any_reflection_file(file_name=mtz_file)
    content = reflection_file.file_content()
    space_group = content.space_group_name().replace(" ", "")
    resolution = content.max_min_resolution()[1]
    cell_parameters = content.crystals()[0].unit_cell_parameters()

    return space_group, resolution, cell_parameters


def get_labels(mtz_file):
    """Function to get the column labels for input mtz file

    Parameters
    ----------
    mtz_file : str
       The path to the mtz file

    Returns
    -------
    f : str
        f column label
    fp : str
        fp column label
    dano : str
        dano column label
    sigdano : str
        sigdano column label
    free : str
        free column label
    """

    reflection_file = reflection_file_reader.any_reflection_file(file_name=mtz_file)
    if not reflection_file.file_type() == "ccp4_mtz":
        msg="File is not of type ccp4_mtz: {0}".format(mtz_file)
        logging.critical(msg)
        raise RuntimeError(msg)

    content = reflection_file.file_content()
    ctypes = content.column_types()
    clabels = content.column_labels()
    ftype = 'F'
    jtype = 'J'
    dtype = 'D'

    if ftype not in ctypes:
        msg = "Cannot find any structure amplitudes in: {0}".format(mtz_file)
        raise RuntimeError(msg)
    f = clabels[ctypes.index(ftype)]

    # FP derived from F
    fp = 'SIG' + f
    if fp not in clabels:
        msg = "Cannot find label {0} in file: {1}".format(fp, mtz_file)
        raise RuntimeError(msg)

    if jtype not in ctypes:
        msg = "Cannot find any intensities in: {0}".format(mtz_file)
        raise RuntimeError(msg)
    i = clabels[ctypes.index(jtype)]

    # SIGI derired from I
    sigi = 'SIG' + i
    if sigi not in clabels:
        msg = "Cannot find label {0} in file: {1}".format(sigi, mtz_file)
        raise RuntimeError(msg)

    try:
        if dtype not in ctypes:
            msg = "Cannot find any structure amplitudes in: {0}".format(mtz_file)
            raise RuntimeError(msg)
        dano = clabels[ctypes.index(dtype)]

        # SIGDANO derived from DANO
        sigdano = 'SIG' + dano
        if sigdano not in clabels:
            msg = "Cannot find label {0} in file: {1}".format(sigdano, mtz_file)
            raise RuntimeError(msg)
    except RuntimeError:
        dano, sigdano = None, None

    free = None
    for label in content.column_labels():
        if 'free' in label.lower():
            column = content.get_column(label=label)
            selection_valid = column.selection_valid()
            flags = column.extract_values()
            sel_0 = (flags == 0)
            # extract number of work/test reflections
            n0 = (sel_0 & selection_valid).count(True)
            n1 = (~sel_0 & selection_valid).count(True)
            if n0 > 0 and n1 > 0:
                if free:
                    logger.warning("FOUND >1 R FREE label in file!")
                free = label

    return f, fp, i, sigi, dano, sigdano, free

