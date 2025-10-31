def _first_ok(import_attempts):
    """Run callables until one returns without ImportError."""
    last = None
    for fn in import_attempts:
        try:
            return fn()
        except ImportError as e:
            last = e
            continue
    if last:
        raise last
    raise ImportError("No import attempts were provided")
