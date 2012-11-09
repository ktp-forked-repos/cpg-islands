""":mod:`cpg_islands.views.qt` --- Views based on Q toolkit
"""

from PySide import QtGui, QtCore

from cpg_islands import metadata
from cpg_islands.views import (BaseAppView,
                               BaseSeqInputView,
                               BaseResultsView)


class AppView(QtGui.QMainWindow, BaseAppView):
    def __init__(self, seq_input_view, results_view, parent=None):
        """Initialize the main application view with docked
        SeqenceInputView and ResultsView.

        :param seqe_input_view: the input view
        :type seq_input_view: :class:`BaseSeqInputView`
        :param results_view: the results view
        :type results_view: :class:`BaseResultsView`
        """
        super(AppView, self).__init__(parent)

        # Menu
        self.menu_bar = QtGui.QMenuBar()
        self.file_menu = self.menu_bar.addMenu('&File')
        self.file_action = self.file_menu.addAction('&Load File')
        self.file_action.triggered.connect(self._load_file)
        self.quit_action = self.file_menu.addAction('&Quit')
        self.quit_action.triggered.connect(self.close)
        self.help_menu = self.menu_bar.addMenu('&Help')
        self.about_action = self.help_menu.addAction('&About')
        self.about_action.triggered.connect(self._about)
        self.setMenuBar(self.menu_bar)

        # Main
        self.central_widget = QtGui.QWidget(self)
        self.layout = QtGui.QHBoxLayout(self.central_widget)
        self.layout.addWidget(seq_input_view)
        self.layout.addWidget(results_view)
        self.setCentralWidget(self.central_widget)

    def start(self):
        self.show()
        self.raise_()

    def _about(self):
        """Create and show the about dialog."""
        AboutDialog(self).exec_()

    def _load_file(self):
        """Create and show the file dialog."""
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            caption='Load GenBank File...',
            filter='GenBank Sequence File (*.gb)')
        self.file_load_requested(file_name[0])


class SeqInputView(QtGui.QWidget, BaseSeqInputView):
    def __init__(self, parent=None):
        super(SeqInputView, self).__init__(parent)

        self.layout = QtGui.QFormLayout(self)
        self.seq_input = QtGui.QPlainTextEdit(self)
        self.seq_input.setTabChangesFocus(True)
        self.layout.addRow('Sequence', self.seq_input)

        self.island_size_input = QtGui.QLineEdit(self)
        self.island_size_validator = QtGui.QIntValidator()
        self.island_size_validator.setBottom(0)
        self.island_size_input.setValidator(self.island_size_validator)
        self.layout.addRow('Island Size', self.island_size_input)

        self.min_gc_ratio_input = QtGui.QLineEdit(self)
        self.min_gc_ratio_validator = QtGui.QDoubleValidator()
        self.min_gc_ratio_validator.setBottom(0)
        self.min_gc_ratio_validator.setTop(1)
        self.min_gc_ratio_input.setValidator(self.min_gc_ratio_validator)
        self.layout.addRow('GC Ratio', self.min_gc_ratio_input)

        self.submit_button = QtGui.QPushButton('Find Islands', self)
        self.submit_button.clicked.connect(self._submit_clicked)
        self.layout.addRow(self.submit_button)

    def _get_seq(self):
        """Return the widget's entered text.

        :return: the text
        :rtype: :class:`str`
        """
        return self.seq_input.toPlainText()

    def set_seq(self, seq_str):
        """Set the sequence text.

        :param seq_str: the sequence in string form
        :type seq_str: :class:`str`
        """
        self.seq_input.setPlainText(seq_str)

    def _get_min_gc_ratio(self):
        """Return the widget's entered GC ratio.

        :return: the key
        :rtype: :class:`str`
        """
        return self.min_gc_ratio_input.text()

    def set_min_gc_ratio(self, min_gc_ratio):
        self.min_gc_ratio_input.setText(min_gc_ratio)

    def _get_island_size(self):
        """Return the widget's entered island size.

        :return: the key
        :rtype: :class:`str`
        """
        return self.island_size_input.text()

    def set_island_size(self, island_size):
        self.island_size_input.setText(island_size)

    def show_error(self, message):
        """Show the user an error dialog.

        :param message: error message
        :type message: :class:`str`
        """
        QtGui.QMessageBox.critical(self, metadata.nice_title, message)

    def _submit_clicked(self):
        try:
            self.submitted(self._get_seq(),
                           self._get_island_size(),
                           self._get_min_gc_ratio())
        except ValueError as error:
            self.show_error(str(error))


class ResultsView(QtGui.QWidget, BaseResultsView):
    def __init__(self, parent=None):
        super(ResultsView, self).__init__(parent)

        self.hbox = QtGui.QHBoxLayout(self)
        self.cpg_list = QtGui.QListWidget(self)
        self.cpg_list.itemActivated.connect(self._item_activated)
        self.cpg_list.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scene = QtGui.QGraphicsScene()
        self.global_seq = AutoZoomGraphicsView(self.scene)

        self.local_seq = QtGui.QPlainTextEdit(self)

        self.sequences = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.sequences.addWidget(self.global_seq)
        self.sequences.addWidget(self.local_seq)
        self.sequences.setSizes([100, 100])

        self.holder = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.holder.addWidget(self.cpg_list)
        self.holder.addWidget(self.sequences)
        self.holder.setSizes([100, 490])

        self.hbox.addWidget(self.holder)

    def set_locations(self, locations):
        """Set encoded text result.

        :param result: the encoded text
        :type locations: :class:`list` of :class:`tuple`
        """
        self.cpg_list.clear()
        for index, (start, end) in enumerate(locations):
            self.cpg_list.insertItem(index, str(start) + ', ' + str(end))

    def _item_activated(self, item):
        index = self.cpg_list.indexFromItem(item).row()
        self.feature_selected(index)

    def set_local_seq(self, local_seq):
        self.local_seq.setPlainText(local_seq)


class AutoZoomGraphicsView(QtGui.QGraphicsView):
    """Graphics view class which auto-resizes the scene."""
    def resizeEvent(self, event):
        """Automatically resize the graphics view to fit the scene.

            :param event: the resize event
            :type event: :class:`PySide.QtGui.QResizeEvent`
            """
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)


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
