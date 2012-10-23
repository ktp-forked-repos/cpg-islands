""":mod:`cpg_islands.models` --- Application models
"""

from __future__ import print_function
import sys
import argparse
import abc

from Bio.Seq import Seq
from Bio.SeqUtils import GC
from Bio.SeqFeature import SeqFeature, FeatureLocation

from cpg_islands import metadata


class InvalidIslandSizeError(Exception):
    def __init__(self, island_size):
        self.island_size = island_size

    def __str__(self):
        return 'Invalid island size: {0}'.format(self.island_size)


class MetaApplicationModel(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self, argv=None):
        pass

    @abc.abstractmethod
    def annotate_cpg_islands(self, seq, island_size, minimum_gc_ratio):
        pass


class ApplicationModel(MetaApplicationModel):
    def run(self, argv=None):
        if argv is None:
            argv = sys.argv

        author_strings = []
        for name, email in zip(metadata.authors, metadata.emails):
            author_strings.append('Author: {0} <{1}>'.format(name, email))

        epilog = '''{title} {version}

{authors}
URL: <{url}>
'''.format(
            title=metadata.nice_title,
            version=metadata.version,
            authors='\n'.join(author_strings),
            url=metadata.url)

        arg_parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=metadata.description,
            epilog=epilog)

        args = arg_parser.parse_args(args=argv[1:])

        print(epilog)

    def annotate_cpg_islands(self, seq, island_size, minimum_gc_ratio):
        if island_size <= 0:
            raise InvalidIslandSizeError(island_size)
        features = []
        if island_size <= len(seq):
            for start_index in xrange(len(seq) - island_size + 1):
                end_index = start_index + island_size
                if GC(seq[start_index:end_index]) > minimum_gc_ratio:
                    feature = SeqFeature(
                        FeatureLocation(start_index, end_index))
                    features.append(feature)
        return features
