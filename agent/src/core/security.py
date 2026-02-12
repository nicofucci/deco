import ssl
import platform
import socket

def get_ssl_context(verify: bool = False) -> ssl.SSLContext:
    """
    Returns an SSL context.
    For MVP/Dev, verify=False allows self-signed certificates.
    In Prod, this should be strict.
    """
    if verify:
        return ssl.create_default_context()
    else:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

def get_system_info() -> dict:
    """
    Returns basic system info for registration.
    """
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "arch": platform.machine(),
        "version": "0.1.0" # Agent Version
    }
