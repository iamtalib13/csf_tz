import frappe

def execute():
    # Check if the "Trade In" item already exists
    trade_in_item = frappe.get_all('Item', filters={'item_code': 'Trade In'}, limit=1)
    
    if not trade_in_item:
        # Create the new Trade In Item
        item = frappe.get_doc({
            'doctype': 'Item',
            'item_code': 'Trade In',
            'item_name': 'Trade In',
            'item_group': 'All Item Groups',  # Set item group to "All Item Groups"
            'stock_uom': 'Nos',  # Set stock unit of measure to "Nos"
            'disabled': 0,
          
        })
        item.insert()
        frappe.db.commit()  # Commit the transaction
        frappe.msgprint("Trade In item created successfully.")
    else:
        frappe.msgprint("Trade In item already exists.")
