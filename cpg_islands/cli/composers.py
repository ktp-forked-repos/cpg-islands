""":mod:`cpg_islands.cli.composers` --- Functions to create CLI MVP triads
"""

from cpg_islands.models import ApplicationModel
from cpg_islands.cli.views import ApplicationView
from cpg_islands.presenters import ApplicationPresenter


def create_presenter(argv):
    """Create a presenter with a command-line view.

    :return: the created presenter
    :rtype: :class:`ApplicationPresenter`
    """
    model = ApplicationModel()
    view = ApplicationView()
    presenter = ApplicationPresenter(model, view)
    presenter.register_for_events()
    model.run(argv)
    return presenter
