# Instance-specific configuration.

# If you're trying to mess around in the code, change this to True.
DEBUG = False

# Key used by Flask to encrypt and sign cookies. It should be basically a few
# random bytes. Replace this value with output from this command:
# $ python -c "import os; print(os.urandom(24));"
SECRET_KEY = b'_______REPLACE_ME_______'

# Which IP/hostname and port to listen on? Set the host to '0.0.0.0' to make
# the app externally visible. (Keep in mind we don't really do auth, okay?)
SERVER_NAME='127.0.0.1:5000'

# libvirt connection URL for the UI to expose: https://libvirt.org/uri.html
# USB attach works only with the default URL (local system QEMU).
LIBVIRT_URL = 'qemu:///system'

# You can forcefully disable USB attach or memory management features here.
DISABLE_USB_ATTACH = False
DISABLE_MEMORY_TWEAKING = False
