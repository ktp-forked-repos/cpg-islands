from Bio.Seq import Seq
from Bio.Alphabet import IUPAC, _verify_alphabet


class AppPresenter(object):
    def __init__(self, model, view):
        """Constructor.

        :param model: application model
        :type model: :class:`MetaAppModel`
        :param view: application view
        :type view: :class:`MetaAppView`
        """
        self.model = model
        self.view = view

    def register_for_events(self):
        self.model.started.append(self.view.start)
        self.view.file_load_requested.append(self.model.load_file)
        self.model.locations_computed.append(self.view.show_results)


class SeqInputPresenter(object):
    def __init__(self, model, view):
        """Constructor.

        :param model: sequence input model
        :type model: :class:`MetaSeqInputModel`
        :param view: sequence input view
        :type view: :class:`MetaSeqInputView`
        """
        self.model = model
        self.view = view

    def register_for_events(self):
        self.model.island_definition_defaults_set.append(
            self._island_definition_defaults_set)
        self.model.file_loaded.append(self.view.set_seq)
        self.view.submitted.append(self._user_submits)
        self.model.error_raised.append(self.view.show_error)

    def _island_definition_defaults_set(self, island_size, min_gc_ratio):
        """Called when island definition defaults are set.

        :param island_size: number of bases in the island
        :type island_size: :class:`int`
        :param min_gc_ratio: minimum ratio of Guanine/Cytosine
        :type min_gc_ratio: :class:`float`
        """
        self.view.set_island_size(str(island_size))
        self.view.set_min_gc_ratio(str(min_gc_ratio))

    def _user_submits(self, seq_str, island_size_str, min_gc_ratio_str):
        """Called when the user submits the form.

        :param seq_str: the sequence as a string
        :type seq_str: :class:`str`
        :param island_size_str: number of bases which an island may contain
        :type island_size_str: :class:`str`
        :param min_gc_ratio_str: the ratio of GC to other bases
        :type min_gc_ratio_str: :class:`str`
        """
        seq_mixed_case = Seq(seq_str, IUPAC.unambiguous_dna)
        seq = seq_mixed_case.upper()
        # Using `_verify_alphabet' is somewhat questionable, since it
        # is marked as private. However, there are no other documented
        # ways to verify the sequence.
        if not _verify_alphabet(seq):
            self.view.show_error(
                '''Sequence letters not within alphabet:
  Alphabet: {0}
  Sequence: {1}'''.format(seq.alphabet.letters, str(seq)))
            return
        try:
            island_size = int(island_size_str)
        except ValueError:
            self.view.show_error(
                'Invalid integer for island size: {0}'.format(island_size_str))
            return
        try:
            min_gc_ratio = float(min_gc_ratio_str)
        except ValueError:
            self.view.show_error(
                'Invalid ratio for GC: {0}'.format(min_gc_ratio_str))
            return
        self.model.annotate_cpg_islands(
            seq, island_size, min_gc_ratio)

    def _file_loaded(self, file_path):
        """Called when the user loads a file.

        :param file_path: the path to the file
        :type file_path: :class:`str`
        """
        try:
            self.view.set_seq(self.model.load_file(file_path))
        except ValueError as error:
            self.view.show_error('Sequence parsing error: {0}'.format(error))


class ResultsPresenter(object):
    def __init__(self, model, view):
        """Constructor.

        :param model: results model
        :type model: :class:`MetaResultsModel`
        :param view: results view
        :type view: :class:`MetaResultsView`
        """
        self.model = model
        self.view = view

    def register_for_events(self):
        self.model.locations_computed.append(self._locations_computed)
        self.view.global_highlight.append(self._get_seq)
        self.view.feature_selected.append(self._get_feature)

    def _locations_computed(self, feature_locations):
        """Called after locations have been computed.

        :param feature_locations: locations of features
        :type feature_locations: :class:`list` of :class:`tuple`
        """
        location_tuples = [(
            f.location.start.position, f.location.end.position)
            for f in feature_locations]
        self.view.set_locations(location_tuples)

    def _get_feature(self, feature_index):
        """Called to get the sequence based on the feature index

        :param feature_index: index of the requested feature
        :type feature_locations: :class:`str`
        """
        feature = self.model.get_feature(feature_index)
        seq = self.model.get_seq()
        self.view.set_local_seq(str(feature.extract(seq)))

    def _get_seq(self):
        """Called to get the sequence based on the feature index

            :param feature_index: index of the requested feature
            :type feature_locations: :class:`str`
            """
        self.view.set_global_seq(self.model.get_seq())
