import frappe

def execute():
    # Get the default company from Global Defaults
    global_defaults = frappe.get_single('Global Defaults')
    default_company = global_defaults.default_company

    # Fetch the abbreviation (abbr) for the default company
    company_details = frappe.get_doc('Company', default_company)
    company_abbr = company_details.abbr

    # Construct the parent account name with the company abbreviation
    parent_account = f'Stock Expenses - {company_abbr}'

    # Check if the "Trade In Control" account already exists using account_name
    control_account = frappe.get_all('Account', filters={'account_name': 'Trade In Control'}, limit=1)

    if not control_account:
        # Create the new Trade In Control Account
        account = frappe.get_doc({
            'doctype': 'Account',
            'account_type': 'Expense Account',  # Specify the type as needed
            'parent_account': parent_account,  # Use the dynamically constructed parent account
            'is_group': 0,
            'company': default_company,  # Use the default company retrieved
            'disabled': 0,
            'account_name': 'Trade In Control',  # Ensure the account name is set
        })
        account.insert()
        frappe.db.commit()  # Commit the transaction
        frappe.msgprint("Trade In Control Account created successfully.")
    else:
        frappe.msgprint("Trade In Control Account already exists.")
