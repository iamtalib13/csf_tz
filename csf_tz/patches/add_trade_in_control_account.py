import frappe

def execute():
    # Get the default company from Global Defaults
    global_defaults = frappe.get_single('Global Defaults')
    default_company = global_defaults.default_company
    
    # Check if the "Trade In Control" account already exists
    control_account = frappe.get_all('Account', filters={'name': 'Trade In Control'}, limit=1)
    
    if not control_account:
        # Create the new Trade In Control Account
        account = frappe.get_doc({
            'doctype': 'Account',
            'name': 'Trade In Control',
            'account_type': 'Expense Account',  # Specify the type as needed
            'parent_account': 'Stock Expenses',  # Change to the appropriate parent account
            'is_group': 0,
            'company': default_company,  # Use the default company retrieved
            'disabled': 0
        })
        account.insert()
        frappe.db.commit()  # Commit the transaction
        frappe.msgprint("Trade In Control Account created successfully.")
    else:
        frappe.msgprint("Trade In Control Account already exists.")
