import frappe

def execute():
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
