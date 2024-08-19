"""
 Namecheap Management library of common functions used by
 all the namecheap execution modules

 Installation Prerequisites
 --------------------------

 - This module uses the following python libraries to communicate to
   the namecheap API:

        * ``requests``
        .. code-block:: bash

            pip install requests

"""

import logging
import xml.dom.minidom

import requests
from salt.exceptions import CommandExecutionError

# Get logging started
log = logging.getLogger(__name__)


def post_request(namecheap_url, opts):
    return _handle_request(requests.post(namecheap_url, data=opts, timeout=45))


def get_request(namecheap_url, opts):
    return _handle_request(requests.get(namecheap_url, params=opts, timeout=45))


def _handle_request(r):
    r.close()

    if r.status_code > 299:
        log.error(str(r))
        raise CommandExecutionError(str(r))

    response_xml = xml.dom.minidom.parseString(r.text)
    apiresponse = response_xml.getElementsByTagName("ApiResponse")[0]

    if apiresponse.getAttribute("Status") == "ERROR":
        data = []
        errors = apiresponse.getElementsByTagName("Errors")[0]
        for e in errors.getElementsByTagName("Error"):
            data.append(e.firstChild.data)
        error = "".join(data)
        log.info(apiresponse)
        log.error(error)
        raise CommandExecutionError(error)

    return response_xml


def xml_to_dict(xml):
    if xml.nodeType == xml.CDATA_SECTION_NODE:
        return xml.data
    result = atts_to_dict(xml)
    if len([n for n in xml.childNodes if n.nodeType != xml.TEXT_NODE]) == 0:
        if len(result) > 0:
            if xml.firstChild is not None and len(xml.firstChild.data) > 0:
                result["data"] = xml.firstChild.data
        elif xml.firstChild is not None and len(xml.firstChild.data) > 0:
            return xml.firstChild.data
        else:
            return None
    elif xml.childNodes.length == 1 and xml.childNodes[0].nodeType == xml.CDATA_SECTION_NODE:
        return xml.childNodes[0].data
    else:
        for n in xml.childNodes:
            if n.nodeType == xml.CDATA_SECTION_NODE:

                if xml.tagName.lower() in result:
                    val = result[xml.tagName.lower()]
                    if not isinstance(val, list):
                        temp = [val]
                        val = temp
                    val.append(n.data)
                    result[xml.tagName.lower()] = val
                else:
                    result[xml.tagName.lower()] = n.data

            elif n.nodeType != xml.TEXT_NODE:

                if n.tagName.lower() in result:
                    val = result[n.tagName.lower()]

                    if not isinstance(val, list):
                        temp = [val]
                        val = temp
                    val.append(xml_to_dict(n))
                    result[n.tagName.lower()] = val
                else:
                    result[n.tagName.lower()] = xml_to_dict(n)
    return result


def atts_to_dict(xml):
    result = {}
    if xml.attributes is not None:
        for key, value in xml.attributes.items():
            result[key.lower()] = string_to_value(value)
    return result


def string_to_value(value):
    temp = value.lower()
    result = None
    if temp == "true":
        result = True
    elif temp == "false":
        result = False
    else:
        try:
            result = int(value)
        except ValueError:
            try:
                result = float(value)
            except ValueError:
                result = value

    return result


def get_opts(config_option, command):
    opts = {}
    opts["ApiUser"] = config_option("namecheap.name")
    opts["UserName"] = config_option("namecheap.user")
    opts["ApiKey"] = config_option("namecheap.key")
    opts["ClientIp"] = config_option("namecheap.client_ip")
    opts["Command"] = command
    return opts, config_option("namecheap.url")
