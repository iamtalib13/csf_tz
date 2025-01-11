
import frappe

def execute():
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
                "is_stock_item": 0,
            })
            item.insert()
            frappe.db.commit()
            print("Trade In item created successfully.")
        else:
            print("Trade In item already exists.")
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Error in Trade-In Item Creation Script")
        print(f"An error occurred: {str(e)}")
