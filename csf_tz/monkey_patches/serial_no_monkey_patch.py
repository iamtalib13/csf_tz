# csf_tz/monkey_patches/serial_no_monkey_patch.py
import frappe
from frappe.utils import now

original_set_value = frappe.db.set_value  # Store original method

def patched_set_value(doctype, name, fieldname, value=None, **kwargs):
    if doctype == "Serial No" and fieldname == "status" and value == "Delivered":
        timestamp = now()

        frappe.db.sql("""
            UPDATE `tabSerial No`
            SET status = %s, modified = %s
            WHERE name = %s
        """, (value, timestamp, name))

        parent = frappe.db.get_value("Serial and Batch Entry", {"serial_no": name}, "parent")
        if parent:
            frappe.db.sql("""
                UPDATE `tabSerial and Batch Bundle`
                SET modified = %s
                WHERE name = %s
            """, (timestamp, parent))

        return True

    return original_set_value(doctype, name, fieldname, value, **kwargs)

frappe.db.set_value = patched_set_value  # Apply patch