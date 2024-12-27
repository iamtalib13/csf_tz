import frappe

def execute():
    # Check if the "Trade In" Item Group exists
    item_group = frappe.get_all('Item Group', filters={'name': 'Trade In'}, limit=1)
    
    # Create "Trade In" Item Group if it doesn't exist
    if not item_group:
        item_group_doc = frappe.get_doc({
            'doctype': 'Item Group',
            'item_group_name': 'Trade In',
            'is_group': 0  # Set to 0 for a non-group item group
        })
        item_group_doc.insert()
        frappe.db.commit()  # Commit the transaction
        print("Item Group 'Trade In' created successfully.")
    
    # Check if the "Trade In" item already exists
    trade_in_item = frappe.get_all('Item', filters={'item_code': 'Trade In'}, limit=1)
    
    if not trade_in_item:
        # Create the new Trade In Item
        item = frappe.get_doc({
            'doctype': 'Item',
            'item_code': 'Trade In',
            'item_name': 'Trade In',
            'item_group': 'Trade In',  # Use the created item group
            'disabled': 0,
        })
        item.insert()
        frappe.db.commit()  # Commit the transaction
        print("Trade In item created successfully.")
    else:
        print("Trade In item already exists.")
