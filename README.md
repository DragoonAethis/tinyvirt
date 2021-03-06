# tinyvirt

An extremely lightweight libvirt web UI that probably doesn't do what you want.

- Turn on/off/suspend/resume VMs.
- Change the allocated maximum/current memory (VMs with memballoon will use the
  new settings instantly, if supported by the VM and libvirt).
- Redirect local USB devices (will not work on remote hosts).

That's it. I needed a small "remote" for my VFIO VMs, and it works great for
that, but will probably not do much more. Contributions are welcome, though!


## Dependencies

- Python 3.6 (w/ virtualenv3) or newer.
- [Flask 1.0](http://flask.pocoo.org/docs/0.12/)
- [flask-classful 0.14](http://flask-classful.teracy.org/)
- [libvirt-python](https://pypi.python.org/pypi/libvirt-python)
- All Python pkgs are installed automatically into a virtualenv with `run.sh`.


## Installation

- `git clone` this repo somewhere. `cd` into its root.
- `mkdir instance && cp tinyvirt/config.py instance/`
- Edit the `instance/config.py` file as needed.
- `./run.sh` and you're done - tinyvirt will start on the provided host.

The `run.sh` script will automatically create a virtualenv and install all the
dependencies required, as specified by `setup.py`. It shouldn't mess with your
system-wide Python installation, but if you install all the dependencies and
run it as a regular WSGI app in Apache or something, it should work just fine.

If you want to run it on boot, you might want to use this unit under systemd:

    [Unit]
    Description=A tiny libvirt management web UI.
    
    [Service]
    Type=simple
    ExecStart=/srv/tinyvirt/run.sh
    WorkingDirectory=/srv/tinyvirt
    
    [Install]
    WantedBy=multi-user.target


## Contributing

All contributions are welcome! I've added just enough features I wanted, so I
probably won't add too much new stuff myself, but if you'd like me to look into
supporting something, create an issue or even contribute the feature. The code
*is* a little bit messy here and there, but it wasn't exactly supposed to be
public until someone asked me about sharing this.

What would be nice to have:

- Security (currently there's none).
- Simple VM creation (turns out *it's a lot of work*).
- Remote device redirection (at the moment it's parsing local `lsusb` output,
  but libvirt exposes something called nodedev - not sure how it's used yet).


## License

This software is available under the MIT license. See the LICENSE file for more
information.
