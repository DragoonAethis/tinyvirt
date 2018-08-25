import json, subprocess, libvirt
from flask import Flask, Response, jsonify, current_app, request, abort, g, render_template, redirect, url_for, flash

server: Flask = Flask(__name__, instance_relative_config=True)
server.config.from_object('tinyvirt.config')
server.config.from_pyfile('config.py')

import tinyvirt.utils

server.add_template_global(tinyvirt.utils.vm_list, name='vm_list')
server.add_template_global(tinyvirt.utils.vm_by_uuid, name='vm_by_uuid')
server.add_template_global(tinyvirt.utils.usb_device_list, name='usb_device_list')
server.add_template_global(tinyvirt.utils.usb_attach_available, name='usb_attach_available')
server.add_template_global(tinyvirt.utils.memory_tweaking_available, name='memory_tweaking_available')

server.add_template_filter(tinyvirt.utils.vm_pretty_name, name='vm_pretty_name')
server.add_template_filter(tinyvirt.utils.vm_get_attached_usb_devices, name='vm_get_attached_usb_devices')

import tinyvirt.machine
tinyvirt.machine.MachineView.register(server)


@server.before_request
def before_request():
    g.virt = libvirt.open(name=server.config['LIBVIRT_URL'])
    if g.virt is None:
        abort('Couldn\'t connect to libvirt - check your configuration, please!')


@server.teardown_request
def teardown_request(exception):
    virt = getattr(g, 'virt', None)
    if virt is not None:
        try:
            g.virt.close()
        except:
            pass  # Whatever, we're quitting!


@server.route('/', methods=['GET', 'POST'])
def index():
    version: int = g.virt.getLibVersion()
    major = int(version / 1000000)
    minor = int((version - major * 1000000) / 1000)
    patch = int(version - major * 1000000 - minor * 1000)
    libvirt_version: str = "{}.{}.{}".format(major, minor, patch)

    caps: str = g.virt.getCapabilities()
    caps.replace("//n", '/n')

    sysinfo: str = g.virt.getSysinfo()
    sysinfo.replace("//n", '/n')

    return render_template("dashboard.html",
                           hostname=g.virt.getHostname(),
                           libvirt_version=libvirt_version,
                           capabilities_xml=caps,
                           sysinfo_xml=sysinfo,
                           max_memory=g.virt.getInfo()[1],
                           free_memory=g.virt.getFreeMemory() / 1048576)


@server.route('/reboot')
def reboot():
    subprocess.Popen("notify-send \"Rebooting!\" && sleep 3 && reboot", stdout=subprocess.PIPE, shell=True, stderr=subprocess.STDOUT)
    flash("Host is now rebooting - refresh this page in a minute or so.")
    return redirect(url_for('index'))


if __name__ == '__main__':
    server.run()
