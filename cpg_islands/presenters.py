from Bio.Seq import Seq
from Bio.Alphabet import IUPAC, _verify_alphabet


class AlphabetError(ValueError):
    """Error raised when invalid bases are present."""
    def __init__(self, sequence_str, alphabet_letters):
        self.sequence_str = sequence_str
        self.alphabet_letters = alphabet_letters

    def __str__(self):
        return '''Sequence letters not within alphabet:
  Alphabet: {0}
  Sequence: {1}'''.format(self.alphabet_letters, self.sequence_str)


class ApplicationPresenter(object):
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def register_for_events(self):
        self.model.started.append(self.view.start)
        self.view.submitted.append(self._user_submits)
        self.view.sequence_changed.append(self._sequence_changed)

    def _user_submits(self, seq_str, island_size_str, minimum_gc_ratio_str):
        """Called when the user submits the form.

        :param seq_str: the sequence as a string
        :type seq_str: :class:`str`
        :param island_size_str: number of bases which an island may contain
        :type island_size_str: :class:`str`
        :param minimum_gc_ratio_str: the ratio of GC to other bases
        :type minimum_gc_ratio_str: :class:`str`
        """
        seq_mixed_case = Seq(seq_str, IUPAC.unambiguous_dna)
        seq = seq_mixed_case.upper()
        # Using `_verify_alphabet' is somewhat questionable, since it
        # is marked as private. However, there are no other documented
        # ways to verify the sequence.
        if not _verify_alphabet(seq):
            raise AlphabetError(str(seq), seq.alphabet.letters)
        try:
            island_size = int(island_size_str)
        except ValueError:
            raise ValueError(
                'Invalid integer for island size: {0}'.format(island_size_str))
        try:
            minimum_gc_ratio = float(minimum_gc_ratio_str)
        except ValueError:
            raise ValueError(
                'Invalid ratio for GC: {0}'.format(minimum_gc_ratio_str))
        locations = self.model.annotate_cpg_islands(seq,
                                                    island_size,
                                                    minimum_gc_ratio)
        location_tuples = [(f.location.start.position,
                            f.location.end.position) for f in locations]
        self.view.set_locations(location_tuples)

    def _sequence_changed(self, sequence_str):
        """Called when the sequence text is changed to sanitize it.

        :param sequence_str: the sequence text
        :type sequence_str: :class:`str`
        """
        self.view.set_sequence(self.model.sanitize_sequence(sequence_str))
