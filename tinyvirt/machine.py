from flask import render_template, redirect, request, url_for, g, abort, flash, jsonify
from flask_classful import FlaskView, route
from libvirt import virDomain
import libvirt

import tinyvirt.utils as utils


class MachineView(FlaskView):
    route_prefix = '/'
    excluded_methods = ['template_function']

    def index(self):
        import tinyvirt
        return tinyvirt.index()  # From tinyvirt.index()

    @route('/<uuid>/attach', endpoint='attach_device', methods=['POST'])
    def attach_device(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        if not utils.usb_attach_available():
            flash("USB device management is not supported in the current configuration.", category='error')
            return redirect(url_for('show_vm', uuid=uuid))

        device = str(request.form['usbDevice'])
        if utils.is_valid_usb_device(device):
            xml = utils.usb_device_to_xml(device)

            status = vm.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            if status != 0:
                flash("Failed to attach the device - is it already attached/occupied?", category='error')
            elif vm.isActive():
                status = vm.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
                if status != 0:
                    flash("Failed to live attach the device - try restarting the VM now to apply.", category='error')
        else:
            flash("The chosen device was invalid - did you remove something while picking one here?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/detach/<device>', endpoint='detach_device', methods=['GET'])
    def detach_device(self, uuid, device):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        if not utils.usb_attach_available():
            flash("USB device management is not supported in the current configuration.", category='error')
            return redirect(url_for('show_vm', uuid=uuid))

        if utils.is_valid_usb_device(device):
            xml = utils.usb_device_to_xml(device)

            status = vm.detachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            if status != 0:
                flash("Failed to detach the device - is it already attached/occupied?", category='error')
            elif vm.isActive():
                status = vm.detachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_LIVE)
                if status != 0:
                    flash("Failed to live detach the device - try restarting the VM now to apply.", category='error')
        else:
            flash("The chosen device was invalid.", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>', endpoint="show_vm")
    def get(self, uuid):
        return render_template('vm.html', selected_vm=utils.vm_by_uuid(uuid))

    @route('/create/', endpoint="create_vm", methods=['GET', 'POST'])
    def create(self):
        if request.method == 'GET':
            return render_template('create_vm.html')
        elif request.method == 'POST':
            return render_template('create_info.html')

    @route('/<uuid>/start', endpoint='start_vm')
    def start(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        state, active = vm.state()
        if not (state | libvirt.VIR_DOMAIN_SHUTDOWN):
            flash("Guest is already up/in a state impossible to start from.", category='warning')
        else:
            status = vm.create()
            if status == 0:
                flash("Guest is booting, please wait...", category='info')
            else:
                flash("Failed to boot guest - check your logs!", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/resume', endpoint='resume_vm')
    def resume(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        state, active = vm.state()
        if state == libvirt.VIR_DOMAIN_PMSUSPENDED:
            active = vm.pMWakeup()
        elif state == libvirt.VIR_DOMAIN_PAUSED:
            active = vm.resume()
        else:
            flash("Guest can't be resumed from this state.", category='warning')
            return redirect(url_for('show_vm', uuid=uuid))

        if active == 0:
            flash("Domain is being resumed, just a moment...", category='info')
        else:
            flash("Resume request failed, try inspecting the guest from virsh?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/stop', endpoint='stop_vm')
    def stop(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        status = vm.shutdown()
        if status == 0:
            flash("Guest is shutting down, this may take a while...", category='info')
        else:
            flash("Shutdown request failed - try forcing power off?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/suspend', endpoint='suspend_vm')
    def suspend(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        status = vm.suspend()
        if status == 0:
            flash("Guest is suspending, this may take a while...", category='info')
        else:
            flash("Suspend request failed! Try suspending/hibernating from console?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/reboot', endpoint='reboot_vm')
    def reboot(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        status = vm.reboot()
        if status == 0:
            flash("Guest is rebooting, this may take a while...", category='info')
        else:
            flash("Reboot request failed! Try rebooting manually from console or force resetting?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/force_reboot', endpoint='force_reboot_vm')
    def force_reboot(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        status = vm.destroy()
        if status == 0:
            return self.start(uuid=uuid)
        else:
            flash("Guest shutdown failed! Try rebooting the host?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/force_off', endpoint='force_off_vm')
    def force_off(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        status = vm.destroy()
        if status == 0:
            flash("Guest killed.", category='info')
        else:
            flash("Guest shutdown failed! Try rebooting the host?", category='error')

        return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/destroy', endpoint='destroy_vm')
    def destroy(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        if vm.isActive():
            status = vm.destroy()
            if status != 0:
                flash("Failed to stop the VM - try to stop it manually first.")
                return redirect(url_for('show_vm', uuid=uuid))

        status = vm.undefine()
        if status == 0:
            flash("VM deleted.", category='info')
            return redirect(url_for('index'))
        else:
            flash("Failed to undefine the VM - inspect it with virt-manager/virsh!")
            return redirect(url_for('show_vm', uuid=uuid))

    @route('/<uuid>/memory', endpoint='view_memory', methods=['GET'])
    def view_memory(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        _, maxMemory, currentMemory, _, _ = vm.info()

        return jsonify({"max-memory": maxMemory, "current-memory": currentMemory})

    @route('/<uuid>/memory', endpoint='edit_memory', methods=['POST'])
    def edit_memory(self, uuid):
        vm: virDomain = utils.vm_by_uuid(uuid)
        abort(404) if vm is None else None

        if utils.memory_tweaking_available():
            flash("Memory tweaking is not available in the current configuration.", category='error')
            return redirect(url_for('show_vm', uuid=uuid))

        try:
            maxMemory = int(request.form['maxMemory'])
            if maxMemory <= 0:
                raise ValueError()
        except:
            flash("Something went wrong while setting new parameters - no changes were made.", category='error')
            return redirect(url_for('show_vm', uuid=uuid))

        try:
            currentMemory = int(request.form['currentMemory'])
            if currentMemory <= 0 or currentMemory >= maxMemory:
                raise ValueError()
        except:
            currentMemory = maxMemory

        try:
            vm.setMemoryFlags(maxMemory * 1024,     libvirt.VIR_DOMAIN_MEM_CONFIG | libvirt.VIR_DOMAIN_MEM_MAXIMUM)
            vm.setMemoryFlags(currentMemory * 1024, libvirt.VIR_DOMAIN_MEM_CONFIG | libvirt.VIR_DOMAIN_MEM_CURRENT)
            flash("Memory parameters set.", category='info')
        except:
            flash("Something went wrong while setting new parameters - some changes might've been made!",
                  category='error')

        if vm.isActive() == 1:
            try:
                vm.setMemoryFlags(maxMemory * 1024,     libvirt.VIR_DOMAIN_MEM_LIVE | libvirt.VIR_DOMAIN_MEM_MAXIMUM)
                vm.setMemoryFlags(currentMemory * 1024, libvirt.VIR_DOMAIN_MEM_LIVE | libvirt.VIR_DOMAIN_MEM_CURRENT)
            except:
                flash("The running VM might not be affected yet and must be restarted for the changes to be applied.", category='info')

        return redirect(url_for('show_vm', uuid=uuid))
