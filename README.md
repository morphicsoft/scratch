# scratch

Scratchpad area for various experimental bits of code.

More "interesting" modules are:

backoff_retry - a Retry class which wraps a callable with backoff/retry behaviour
chunked_iteration - iterate any iterable in chunks of fixed or varying size
demux - to be combined into logger in order to enable a multiplexed log channel
dependency_decorators - an idea around inter-class dependency declaration & injection
despatch_decorators - a nascent version of observer pattern using decorators for event handler registration
layeredayeaye - a class to enable property-like access to nested dictionaries, which maintains immutable "layers" (is pickleable)
logger / logger2 - a hierarchical logging framework which works across multiprocess boundaries
memoize - a basic memoization decorator
string_template - use pystache to enable a templated self-referential dictionary
