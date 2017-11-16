# Instance-specific configuration.

# If you're trying to mess around in the code, change this to True.
DEBUG = False

# Key used by Flask to encrypt and sign cookies. It should be basically a few
# random bytes. Replace this value with output from this command:
# $ python -c "import os; print(os.urandom(24));"
SECRET_KEY = b'\x00+}\xe2<1A\x88x<\xdb\xa4A=\x16\xa3\xd8_\x97\xbejt\x17\xf5'

# libvirt connection URL for the UI to expose: https://libvirt.org/uri.html
LIBVIRT_URL = 'qemu:///system'
