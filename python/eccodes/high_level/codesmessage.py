"""
``CodesMessage`` class that implements a message readable by ecCodes that
allows access to the message's key-value pairs in a dictionary-like manner
and closes the message when it is no longer needed, coordinating this with
its host file.

Author: Daniel Lee, DWD, 2016
"""

from .. import eccodes


class CodesMessage(object):

    """
    An abstract class to specify and/or implement common behavior that
    messages read by ecCodes should implement.
    """

    #: ecCodes enum-like PRODUCT constant
    product_kind = None

    def __init__(self, codes_file=None, clone=None, sample=None,
                 headers_only=False, other_args_found=False):
        """
        Open a message and inform the host file that it's been incremented.

        If ``codes_file`` is not supplied, the message is cloned from
        ``CodesMessage`` ``clone``. If neither is supplied,
        the ``CodesMessage`` is cloned from ``sample``.

        :param codes_file: A file readable for ecCodes
        :param clone: A valid ``CodesMessage``
        :param sample: A valid sample path to create ``CodesMessage`` from
        """
        if (not other_args_found and codes_file is None and clone is None and
                    sample is None):
            raise RuntimeError("CodesMessage initialization parameters not "
                               "present.")
        #: Unique ID, for ecCodes interface
        self.codes_id = None
        #: File containing message
        self.codes_file = None
        if codes_file is not None:
            self.codes_id = eccodes.codes_new_from_file(
                codes_file.file_handle, self.product_kind, headers_only)
            if self.codes_id is None:
                raise IOError("CodesFile %s is exhausted" % codes_file.name)
            self.codes_file = codes_file
            self.codes_file.message += 1
            self.codes_file.open_messages.append(self)
        elif clone is not None:
            self.codes_id = eccodes.codes_clone(clone.codes_id)
        elif sample is not None:
            self.codes_id = self.new_from_sample(sample)

    def write(self, outfile=None):
        """Write message to file."""
        if not outfile:
            # This is a hack because the API does not accept inheritance
            outfile = self.codes_file.file_handle
        eccodes.codes_write(self.codes_id, outfile)

    def __setitem__(self, key, value):
        """
        Set value associated with key.

        Iterables and scalars are handled intelligently.
        """
        # Passed value is iterable and not string
        if hasattr(value, "__iter__"):
            eccodes.codes_set_array(self.codes_id, key, value)
        else:
            eccodes.codes_set(self.codes_id, key, value)

    def keys(self, namespace=None):
        """Get available keys in message."""
        iterator = eccodes.codes_keys_iterator_new(self.codes_id,
                                                   namespace=namespace)
        keys = []
        while eccodes.codes_keys_iterator_next(iterator):
            key = eccodes.codes_keys_iterator_get_name(iterator)
            keys.append(key)
        eccodes.codes_keys_iterator_delete(iterator)
        return keys

    def size(self):
        """Return size of message in bytes."""
        return eccodes.codes_get_message_size(self.codes_id)

    def dump(self):
        """Dump message's binary content."""
        return eccodes.codes_get_message(self.codes_id)

    def get(self, key, ktype=None):
        """Get value of a given key as its native or specified type."""
        if self.missing(key):
            raise KeyError("Key is missing from message.")
        if eccodes.codes_get_size(self.codes_id, key) > 1:
            ret = eccodes.codes_get_array(self.codes_id, key, ktype)
        else:
            ret = eccodes.codes_get(self.codes_id, key, ktype)
        return ret

    def missing(self, key):
        """Report if key is missing."""
        return bool(eccodes.codes_is_missing(self.codes_id, key))

    def set_missing(self, key):
        """Set a key to missing."""
        eccodes.codes_set_missing(self.codes_id, key)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release message handle and inform host file of release."""
        eccodes.codes_release(self.codes_id)

    def __enter__(self):
        return self

    def close(self):
        """Possibility to manually close message."""
        self.__exit__(None, None, None)

    def __contains__(self, key):
        """Check whether a key is present in message."""
        return key in self.keys()

    def __len__(self):
        """Return key count."""
        return len(self.keys())

    def __getitem__(self, key):
        """Return value associated with key as its native type."""
        return self.get(key)

    def __iter__(self):
        return iter(self.keys())

    # Not yet implemented
    # def itervalues(self):
    #    return self.values()

    def items(self):
        """Return list of tuples of all key/value pairs."""
        return [(key, self[key]) for key in self.keys()]

