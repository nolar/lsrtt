from __future__ import absolute_import


def ichunk(src, n):
    """ Iterate over the source, and yield chunks of values of size N. """
    chunk = []
    for idx, val in enumerate(src, 1):
        chunk.append(val)
        if idx % n == 0:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
