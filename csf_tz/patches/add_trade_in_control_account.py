import frappe

def execute():
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
