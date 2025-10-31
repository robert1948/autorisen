from ._shim_utils import _first_ok

create_access_token = _first_ok([
    lambda: __import__("backend.src.modules.auth.tokens", fromlist=["create_access_token"]).create_access_token,
    lambda: __import__("backend.src.modules.auth.auth", fromlist=["create_access_token"]).create_access_token,
])

verify_password = _first_ok([
    lambda: __import__("backend.src.modules.auth.security", fromlist=["verify_password"]).verify_password,
    lambda: __import__("backend.src.modules.auth.auth", fromlist=["verify_password"]).verify_password,
])

get_password_hash = _first_ok([
    lambda: __import__("backend.src.modules.auth.security", fromlist=["get_password_hash"]).get_password_hash,
    lambda: __import__("backend.src.modules.auth.auth", fromlist=["get_password_hash"]).get_password_hash,
])
