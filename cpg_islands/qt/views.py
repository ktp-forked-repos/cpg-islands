""":mod:`cpg_islands.views.qt` --- Views based on Q toolkit
"""

from PySide import QtGui

from cpg_islands import metadata
from cpg_islands.views import (BaseApplicationView,
                               BaseSequenceInputView,
                               BaseResultsView)


class ApplicationView(QtGui.QMainWindow, BaseApplicationView):
    """Primary application view."""

    def __init__(self, sequence_input_view, results_view, parent=None):
        """Construct a main view.

        :param parent: widget parent
        :type parent: :class:`QtGui.QWidget`
        """
        super(ApplicationView, self).__init__(parent)

        # Menu
        self.menu_bar = QtGui.QMenuBar()
        self.file_menu = self.menu_bar.addMenu('&File')
        self.file_action = self.file_menu.addAction('&Load File')
        self.file_action.triggered.connect(self.load_file)
        self.quit_action = self.file_menu.addAction('&Quit')
        self.quit_action.triggered.connect(self.close)
        self.help_menu = self.menu_bar.addMenu('&Help')
        self.about_action = self.help_menu.addAction('&About')
        self.about_action.triggered.connect(self.about)
        self.setMenuBar(self.menu_bar)

        # Main
        self.central_widget = QtGui.QWidget(self)
        self.layout = QtGui.QHBoxLayout(self.central_widget)
        self.layout.addWidget(sequence_input_view)
        self.layout.addWidget(results_view)
        self.setCentralWidget(self.central_widget)


    def start(self):
        """Show and raise the window."""
        self.show()
        self.raise_()

    def about(self):
        """Create and show the about dialog."""
        AboutDialog(self).exec_()

    def load_file(self):
        """Create and show the file dialog."""
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            caption='Load GenBank File...',
            filter='GenBank Sequence File (*.gb)')
        self.file_load_requested(file_name[0])

class AboutDialog(QtGui.QDialog):
    """Shows information about the program."""
    def __init__(self, parent=None):
        """Construct the dialog.

            :param parent: the widget's parent
            :type parent: :class:`QtGui.QWidget`
            """
        super(AboutDialog, self).__init__(parent)
        self.setWindowTitle('About ' + metadata.nice_title)
        self.layout = QtGui.QVBoxLayout(self)
        self.title_label = QtGui.QLabel(metadata.nice_title, self)
        self.layout.addWidget(self.title_label)
        self.version_label = QtGui.QLabel('Version ' + metadata.version, self)
        self.layout.addWidget(self.version_label)
        self.copyright_label = QtGui.QLabel('Copyright (C) ' +
                                            metadata.copyright, self)
        self.layout.addWidget(self.copyright_label)
        self.url_label = QtGui.QLabel(
            'Source: <a href="{0}">{0}</a>'.format(metadata.url), self)
        self.url_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.url_label)
        self.documentation_label = QtGui.QLabel(
            'Documentation: <a href="{0}">{0}</a>'.format(
            metadata.documentation_url), self)
        self.documentation_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.documentation_label)

class SequenceInputView(QtGui.QWidget, BaseSequenceInputView):
    def __init__(self, parent=None):
        super(SequenceInputView, self).__init__(parent)

        self.layout = QtGui.QFormLayout(self)
        self.sequence_input = QtGui.QPlainTextEdit(self)
        self.sequence_input.setTabChangesFocus(True)
        self.layout.addRow('Sequence', self.sequence_input)

        self.island_size_input = QtGui.QLineEdit(self)
        self.island_size_validator = QtGui.QIntValidator()
        self.island_size_validator.setBottom(0)
        self.island_size_input.setValidator(self.island_size_validator)
        self.layout.addRow('Island Size', self.island_size_input)

        self.gc_ratio_input = QtGui.QLineEdit(self)
        self.gc_ratio_validator = QtGui.QDoubleValidator()
        self.gc_ratio_validator.setBottom(0)
        self.gc_ratio_validator.setTop(1)
        self.gc_ratio_input.setValidator(self.gc_ratio_validator)
        self.layout.addRow('GC Ratio', self.gc_ratio_input)

        self.submit_button = QtGui.QPushButton('Find Islands', self)
        self.submit_button.clicked.connect(self._submit_clicked)
        self.layout.addRow(self.submit_button)

    def get_sequence(self):
        """Return the widget's entered text.

        :return: the text
        :rtype: :class:`str`
        """
        return self.sequence_input.toPlainText()

    def set_sequence(self, sequence_str):
        """Set the sequence text.

        :param sequence_str: the sequence in string form
        :type sequence_str: :class:`str`
        """
        self.sequence_input.setPlainText(sequence_str)

    def get_gc_ratio(self):
        """Return the widget's entered GC ratio.

        :return: the key
        :rtype: :class:`str`
        """
        return self.gc_ratio_input.text()

    def get_island_size(self):
        """Return the widget's entered island size.

        :return: the key
        :rtype: :class:`str`
        """
        return self.island_size_input.text()

    def show_error(self, message):
        """Show the user an error dialog.

        :param message: error message
        :type message: :class:`str`
        """
        QtGui.QMessageBox.critical(self, metadata.nice_title, message)

    def _submit_clicked(self):
        try:
            self.submitted(self.get_sequence(),
                           self.get_island_size(),
                           self.get_gc_ratio())
        except ValueError as error:
            self.show_error(str(error))


class ResultsView(QtGui.QWidget, BaseResultsView):
    def __init__(self, parent=None):
        super(ResultsView, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout(self)
        self.result_output = QtGui.QPlainTextEdit(self)
        self.result_output.setReadOnly(True)
        self.layout.addWidget(self.result_output)

    def set_locations(self, locations):
        """Set encoded text result.

        :param result: the encoded text
        :type locations: :class:`list` of :class:`tuple`
        """
        result_list = []
        for start, end in locations:
            result_list.append('{0} {1}'.format(start, end))
            self.result_output.setPlainText('\n'.join(result_list))
