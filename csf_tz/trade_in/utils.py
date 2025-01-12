import frappe

def add_trade_in_module():
    # Check if the "Trade In" module already exists
    trade_in_module = frappe.get_all('Module Def', filters={'module_name': 'Trade In'}, limit=1)
    
    if not trade_in_module:
        # Create the new Trade In Module
        module = frappe.get_doc({
            'doctype': 'Module Def',
            'module_name': 'Trade In',
            'app_name': 'csf_tz',
        })
        module.insert()
        frappe.db.commit()  # Commit the transaction
        print("Trade In Module created successfully.")
    else:
        print("Trade In Module already exists.")

def add_trade_in_item():
    try:
        # Check if the "All Item Groups" Item Group exists
        item_group = frappe.get_all('Item Group', filters={'name': 'All Item Groups'}, limit=1)
        
        if not item_group:
            # Skip item creation if the Item Group does not exist
            print("Item Group 'All Item Groups' does not exist. Skipping item creation.")
            return

        # Check if the "Trade In" item already exists
        trade_in_item = frappe.get_all('Item', filters={'item_code': 'Trade In'}, limit=1)
        
        if not trade_in_item:
            item = frappe.get_doc({
                'doctype': 'Item',
                'item_code': 'Trade In',
                'item_name': 'Trade In',
                'item_group': 'All Item Groups',  
                'stock_uom': 'Nos',
                'disabled': 0,
            })
            item.insert()
            frappe.db.commit()
            print("Trade In item created successfully.")
        else:
            print("Trade In item already exists.")
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Error in Trade-In Item Creation Script")
        print(f"An error occurred: {str(e)}")


def add_trade_in_control_account():
    # Get the default company from Global Defaults
    global_defaults = frappe.get_single('Global Defaults')
    default_company = global_defaults.default_company

    if not default_company:
        frappe.throw("Default company is not set in Global Defaults.")

    # Fetch the abbreviation (abbr) for the default company
    company_details = frappe.get_doc('Company', default_company)
    company_abbr = company_details.abbr

    # Define account names
    stock_expenses_account = f'Stock Expenses - {company_abbr}'
    trade_in_control_account = f'Trade In Control - {company_abbr}'
    direct_expenses_account = f'Direct Expenses - {company_abbr}'

    # Check if "Stock Expenses - {company_abbr}" exists
    if not frappe.db.exists('Account', {'account_name': stock_expenses_account, 'company': default_company}):
        try:
            # Create "Stock Expenses" under "Direct Expenses - {company_abbr}"
            stock_expenses_doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': 'Stock Expenses',  # No abbreviation here
                'is_group': 1,
                'company': default_company,
                'parent_account': direct_expenses_account,  # Check with abbreviation
            })
            stock_expenses_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Parent account 'Stock Expenses' created successfully.")
        except frappe.DuplicateEntryError:
            print(f"'Stock Expenses - {company_abbr}' already exists (avoiding duplicate creation).")

    # Check if "Trade In Control - {company_abbr}" exists
    if not frappe.db.exists('Account', {'account_name': trade_in_control_account, 'company': default_company}):
        try:
            # Create "Trade In Control" under "Stock Expenses - {company_abbr}"
            trade_in_control_doc = frappe.get_doc({
                'doctype': 'Account',
                'account_name': 'Trade In Control',  # No abbreviation here
                'account_type': 'Expense Account',
                'is_group': 0,
                'company': default_company,
                'parent_account': stock_expenses_account,  # Check with abbreviation
                'disabled': 0,
            })
            trade_in_control_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Trade In Control Account 'Trade In Control' created successfully.")
        except frappe.DuplicateEntryError:
            print(f"'Trade In Control - {company_abbr}' already exists (avoiding duplicate creation).")
    else:
        print(f"Trade In Control Account 'Trade In Control' already exists.")


def delete_trade_in_item_and_account():
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

