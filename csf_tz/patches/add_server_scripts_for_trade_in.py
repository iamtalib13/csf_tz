import frappe

def execute():
    # Define the server scripts to be created
    scripts = [
        {
            "doctype_event": "After Submit",
            "name": "Trade In Stock Entry",
            "script": """
# Initialize an empty list to store items
items_list = []

# Fetching Company's Trade_in_control_account from Company
trade_in_control_account = frappe.db.get_value('Company', doc.company, 'custom_trade_in_control_Account')

# Iterate through the items in the document
for item in doc.items:
    if item.get("custom_trade_in_item") and item.get("custom_trade_in_qty"):
        # Check if custom_trade_in_batch_no exists
        custom_batch_no = item.get("custom_trade_in_batch_no")

        if custom_batch_no:
            # Check if a Batch with this ID already exists
            batch_exists = frappe.db.exists("Batch", {"batch_id": custom_batch_no})
            if not batch_exists:
                # Create a new batch with the given custom_trade_in_batch_no
                batch_doc = frappe.new_doc("Batch")
                batch_doc.item = item.get("custom_trade_in_item")
                batch_doc.batch_id = custom_batch_no  # Use the provided custom batch number
                batch_doc.save()

        # Append each item's details to the items_list
        items_list.append({
            "item_code": item.get("custom_trade_in_item"),
            "qty": item.get("custom_trade_in_qty"),
            "uom": "nos",
            "basic_rate": item.get("custom_trade_in_incoming_rate"),
            "batch_no": custom_batch_no,  # Use the custom batch number here
            "serial_no": item.get("custom_trade_in_serial_no"),  # Get custom serial number value
            "expense_account": trade_in_control_account,
        })

# Create a single stock entry if there are items to add
if items_list:
    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt",
        "to_warehouse": "Stores - TC",
        "items": items_list,  # Use the populated list here
        "custom_sales_invoice": doc.name,  # Set the parent field here
    })

    stock_entry.insert()
    stock_entry.submit()

    # Stock Entry
    frappe.msgprint(f"Stock Entry {stock_entry.name} created successfully!")
else:
    frappe.msgprint("No valid items found for stock entry.")
            """,
            "module": "Trade In"
        },
        {
            "doctype_event": "Before Validate",
            "name": "Trade In Serial No and Batch Validation",
            "script": """
# Initialize a list to collect error messages
error_messages = []

# Iterate through the rows of the child table
for row in doc.items:
    # Check if item_code is "Trade In"
    if row.item_code == "Trade In" and row.custom_trade_in_item:
        # Validate batch number if the item requires it
        has_batch_no = frappe.db.get_value("Item", row.custom_trade_in_item, "has_batch_no")
        if has_batch_no and not row.custom_trade_in_batch_no:
            error_messages.append(f"Batch No. is mandatory for Item {row.custom_trade_in_item} in row {row.idx}.")
        
        # Validate serial numbers if the item requires them
        has_serial_no = frappe.db.get_value("Item", row.custom_trade_in_item, "has_serial_no")
        if has_serial_no:
            if not row.custom_trade_in_serial_no:
                error_messages.append(f"Serial Numbers are mandatory for Item {row.custom_trade_in_item} in row {row.idx}.")
            else:
                # Split serial numbers by newline and validate the count
                serial_numbers = row.custom_trade_in_serial_no.split("\\n")
                if len(serial_numbers) != row.custom_trade_in_qty:
                    error_messages.append(
                        f"Serial Numbers count ({len(serial_numbers)}) does not match "
                        f"the Trade-In Quantity ({row.custom_trade_in_qty}) for Item {row.custom_trade_in_item} in row {row.idx}."
                    )

# If there are any errors, raise them all at once
if error_messages:
    frappe.throw(
        title="Validation Errors",
        msg="<br>".join(error_messages),
    )
            """,
            "module": "Trade In"
        },
        {
            "doctype_event": "Before Validate",
            "name": "Trade In Sales Percentage Validation",
            "script": """
# Calculate the total trade-in value from the child table where item_code = "Trade In"
total_trade_in_value = sum(
    row.custom_total_trade_in_value for row in doc.items if row.item_code == "Trade In"
)

# Calculate the total for items in the child table where item_code != "Trade In" using the "amount" field
non_trade_in_total = sum(
    row.amount for row in doc.items if row.item_code != "Trade In"
)

# Fetch allowed percentage from the Company doctype
trade_in_percentage = frappe.db.get_value("Company", doc.company, "custom_trade_in_sales_percentage") or 0

# Calculate the allowed trade-in value based on the percentage of non-trade-in total
allowed_trade_in_value = (trade_in_percentage / 100) * non_trade_in_total

# Validate total trade-in value
if total_trade_in_value > allowed_trade_in_value:
    # Throw error if child table total exceeds the allowed limit
    frappe.throw(
        title="Trade-In Value Validation Error",
        msg=(
            f"Total Trade-In Value ({frappe.format_value(total_trade_in_value)}) exceeds the allowed limit. "
            f"The allowed limit is {trade_in_percentage}% of the total value of non-Trade-In items in the Sales Invoice. "
            f"Maximum allowed Trade-In Value: {frappe.format_value(allowed_trade_in_value)}."
        )
    )
            """,
            "module": "Trade In"
        }
    ]

        # Create or update server scripts
    for script in scripts:
        # Check if the script already exists
        existing_script = frappe.db.exists("Server Script", {"name": script["name"]})
        
        if existing_script:
            # Update the existing script
            existing_doc = frappe.get_doc("Server Script", existing_script)
            existing_doc.script = script["script"]
            existing_doc.module = script["module"]
            existing_doc.reference_doctype = "Sales Invoice"  # Corrected attribute name
            existing_doc.save()
            
        else:
            # Create a new script
            new_doc = frappe.new_doc("Server Script")
            new_doc.update({
                "doctype_event": script["doctype_event"],
                "name": script["name"],
                "script": script["script"],
                "module": script["module"],
                "disabled": 0,
                "allow_guest": 0,
                "api_method": None,
                "cron_format": None,
                "event_frequency": "All",
                "docstatus": 0,
                "reference_doctype": "Sales Invoice"  # Corrected attribute name
            })
            new_doc.insert()
