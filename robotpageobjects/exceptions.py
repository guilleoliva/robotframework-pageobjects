class DuplicateKeyError(ValueError):
    """
    Raised when two selector dictionaries are merged and have a
    duplicate key.
    """
    pass

class KeyOverrideError(Warning):
    """
    Raised when a subclass attempts to override a parent's selector
    without using the Override class.
    """
    pass


class NoBaseUrlError(AttributeError):
    """
    Raised when no baseurl is set for the page object. A baseurl
    must always be set and url/uri_template attributes must be relative
    URIs.
    """
    pass


class NoUriAttributeError(AttributeError):
    """
    Raised when nothing is passed to a page object's open method
    but no url attribute is set on the page object.
    """
    pass


class AbsoluteUriAttributeError(ValueError):
    """
    Raised when nothing is passed to a page object's open
    method and the page object's `url` attribute is set to an
    absolute URL.
    """
    pass


class AbsoluteUriTemplateError(ValueError):
    """
    Raised when a uri_template attribute on a page object is
    set to an absolute URL.
    """
    pass


class InvalidUriTemplateVariableError(ValueError):
    """
    Raised when a variable passed to a page object's open
    method doesn't match a variable in the page object's
    `uri_template` attribute.
    """
    pass


class VarFileImportErrorError(ImportError):
    """
    Raised when a variable file can't be imported
    """
    pass


class MissingSauceOptionError(ValueError):
    """
    Raised when there's a missing sauce option 
    """
    pass
