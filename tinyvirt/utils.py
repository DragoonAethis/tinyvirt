import libvirt, xml.etree.ElementTree as ET
from flask import g
from typing import List


def vm_list() -> List[libvirt.virDomain]:
    domains = g.virt.listAllDomains(0)
    if domains is None:
        return []  # No domains found, get us an empty list.
    else:
        return domains


def vm_by_uuid(uuid: str) -> libvirt.virDomain:
    domains = vm_list()
    for vm in domains:
        if vm.UUIDString() == uuid:
            return vm

    print("Couldn't find:" + str(uuid))
    return None  # Haven't found any matching VM...


def vm_pretty_name(domain: libvirt.virDomain) -> str:
    try:
        return domain.metadata(libvirt.VIR_DOMAIN_METADATA_TITLE, None, libvirt.VIR_DOMAIN_AFFECT_CURRENT)
    except:
        pass

    try:
        return domain.name()
    except:
        pass

    try:
        return domain.UUIDString()
    except:
        pass

    return "[???]"


def usb_attach_available() -> bool:
    from tinyvirt import server

    if server.config['DISABLE_USB_ATTACH'] == True:
        return False

    if server.config['LIBVIRT_URL'] == 'qemu:///system':
        return True  # We can only discover local devices...

    return False

def memory_tweaking_available() -> bool:
    from tinyvirt import server

    if server.config['DISABLE_MEMORY_TWEAKING'] == True:
        return False

    return True


def usb_device_list() -> List[dict]:
    if not usb_attach_available():
        return []

    import subprocess, re
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    lsusb = str(subprocess.check_output("lsusb")).replace("\\n", '\n')
    devices = []
    for line in lsusb.split('\n'):
        if line:
            info = device_re.match(line)
            if info:
                devices.append(info.groupdict())

    return devices


def is_valid_usb_device(usb_id: str) -> bool:
    devices = usb_device_list()
    for device in devices:
        if device['id'] == usb_id:
            return True

    return False  # Not found in local devices...


def usb_device_to_xml(usb_id: str) -> str:
    ven_prod = usb_id.split(':')
    return "<hostdev mode=\"subsystem\" type=\"usb\" managed=\"yes\"><source>" \
        "<vendor id=\"0x{}\"/>" \
        "<product id=\"0x{}\"/>" \
        "</source></hostdev>".format(ven_prod[0], ven_prod[1])


def usb_find_device_name_in_list(device_list: List[dict], vendor: str, product: str) -> dict:
    for device in device_list:
        if device['id'] == vendor + ':' + product:
            return device['tag']

    return "Unknown device"


def vm_get_attached_usb_devices(vm: libvirt.virDomain) -> List[str]:
    all_devices = usb_device_list()
    attached_devices = []

    xml: str = vm.XMLDesc(libvirt.VIR_DOMAIN_XML_SECURE | libvirt.VIR_DOMAIN_XML_INACTIVE)
    xml.replace("\\n", '\n')
    tree: ET.Element = ET.fromstring(xml)

    for hostdev in tree.iter('hostdev'):
        if hostdev.attrib['type'] != 'usb':
            continue

        vendor: str = hostdev.find('source').find('vendor').attrib['id'].split('x')[1]
        product: str = hostdev.find('source').find('product').attrib['id'].split('x')[1]

        device = {
            "vendor": vendor,
            "product": product,
            "tag": usb_find_device_name_in_list(all_devices, vendor, product)
        }

        attached_devices.append(device)

    return attached_devices
