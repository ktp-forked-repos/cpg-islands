from mock import create_autospec, sentinel, call
import pytest
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

from cpg_islands.models import MetaSeqInputModel
from cpg_islands.views import BaseSeqInputView
from cpg_islands.presenters import SeqInputPresenter


@pytest.fixture
def presenter():
    mock_model = create_autospec(MetaSeqInputModel, spec_set=True)
    mock_view = create_autospec(BaseSeqInputView, spec_set=True)
    return SeqInputPresenter(mock_model, mock_view)


class TestSeqInputPresenter:
    def test_register_for_events(self, presenter):
        presenter.register_for_events()
        assert (presenter.model.mock_calls ==
                [call.file_loaded.append(presenter.view.set_seq),
                 call.error_raised.append(presenter.view.show_error)])
        assert (presenter.view.mock_calls ==
                [call.submitted.append(presenter._user_submits)])

    class TestUserSubmits:
        def test_valid_values(self, presenter):
            """When the user clicks submit with valid values, the island
            locations are shown."""
            seq_str = 'ATATGCGCATAT'
            presenter._user_submits(seq_str, '4', '0.5')
            seq = Seq(seq_str, IUPAC.unambiguous_dna)
            # we cannot use assert_called_once_with or mock_cals because
            # these two Seq's use object comparison, and therefore are not
            # "equal"
            assert presenter.model.annotate_cpg_islands.call_count == 1
            # call_args[0] is ordered arguments, call_args[1] is
            # keyword arguments
            annotate_args = presenter.model.annotate_cpg_islands.call_args[0]
            assert len(annotate_args) == 3
            assert str(annotate_args[0]) == str(seq)
            assert annotate_args[1] == 4
            assert annotate_args[2] == 0.5
            assert presenter.view.mock_calls == []

        def test_invalid_sequence(self, presenter):
            """When the user submits a sequence that does not contain
            valid bases, they are shown an error."""
            presenter._user_submits('ABCD', '3', '0.5')
            assert (presenter.view.mock_calls == [call.show_error(
                'Sequence letters not within alphabet:\n'
                '  Alphabet: GATC\n'
                '  Sequence: ABCD')])
            assert presenter.model.mock_calls == []

        def test_invalid_island_size_type(self, presenter):
            """When the user submits an invalid type of island size, they
            are shown an error."""
            presenter._user_submits('ATATGCGC', 'invalid size', '0.5')
            assert (presenter.view.mock_calls ==
                    [call.show_error(
                        'Invalid integer for island size: invalid size')])
            assert presenter.model.mock_calls == []

        def test_invalid_gc_type(self, presenter):
            """When the user submits an invalid type for GC ratio, they
            are shown an error.
            """
            presenter._user_submits('ATATGCGC', '3', 'invalid gc')
            assert (presenter.view.mock_calls ==
                    [call.show_error('Invalid ratio for GC: invalid gc')])
            assert presenter.model.mock_calls == []

        def test_lowercase_sequence(self, presenter):
            """When the user submits a sequence with lowercase letters,
            these should be gracefully handled."""
            seq_str = 'ATatgcGCAtaT'
            presenter._user_submits(seq_str, '4', '0.5')
            seq = Seq('ATATGCGCATAT', IUPAC.unambiguous_dna)
            assert presenter.model.annotate_cpg_islands.call_count == 1
            annotate_args = presenter.model.annotate_cpg_islands.call_args[0]
            assert len(annotate_args) == 3
            assert str(annotate_args[0]) == str(seq)
            assert annotate_args[1] == 4
            assert annotate_args[2] == 0.5
            assert presenter.view.mock_calls == []

    class TestLoadFile:
        def test_valid_sequence(self, presenter):
            presenter.model.load_file.return_value = sentinel.file_contents
            presenter._file_loaded(sentinel.file_path)
            assert (presenter.model.mock_calls ==
                    [call.load_file(sentinel.file_path)])
            assert (presenter.view.mock_calls ==
                    [call.set_seq(sentinel.file_contents)])

        def test_invalid_sequence(self, presenter):
            presenter.model.load_file.side_effect = ValueError(
                'this is a fake message')
            presenter._file_loaded(sentinel.file_path)
            assert (presenter.model.mock_calls ==
                    [call.load_file(sentinel.file_path)])
            assert (presenter.view.mock_calls ==
                    [call.show_error(
                        'Sequence parsing error: this is a fake message')])