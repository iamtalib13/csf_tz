from __future__ import unicode_literals
import frappe

def execute():
    # Get the default company from Global Defaults
    global_defaults = frappe.get_single('Global Defaults')
    default_company = global_defaults.default_company

    if not default_company:
        frappe.throw("Default company is not set in Global Defaults.")

    # Fetch the abbreviation for the default company
    company_details = frappe.get_doc('Company', default_company)
    company_abbr = company_details.abbr

    # Define account name and item name based on the abbreviation
    trade_in_control_account = f'Trade In Control - {company_abbr}'
    trade_in_item = "Trade In"

    # Delete Trade In Control account if it exists
    if frappe.db.exists('Account', {'account_name': trade_in_control_account, 'company': default_company}):
        try:
            frappe.delete_doc('Account', trade_in_control_account)
            print(f"{trade_in_control_account} account has been deleted.")
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Error deleting {trade_in_control_account}")
            print(f"Failed to delete {trade_in_control_account}: {str(e)}")
    else:
        print(f"{trade_in_control_account} account does not exist.")

    # Delete Trade In item if it exists
    if frappe.db.exists('Item', trade_in_item):
        try:
            frappe.delete_doc('Item', trade_in_item)
            print(f"{trade_in_item} has been deleted.")
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Error deleting {trade_in_item}")
            print(f"Failed to delete {trade_in_item}: {str(e)}")
    else:
        print(f"{trade_in_item} does not exist.")
