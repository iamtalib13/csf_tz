import frappe

def execute():
    # Check if the "Trade In Child Table" Client Script already exists
    client_script = frappe.get_all(
        "Client Script",
        filters={"name": "Trade In Child Table"},
        fields=["name"]
    )
    
    if not client_script:
        # Create the new Client Script
        doc = frappe.get_doc({
            "doctype": "Client Script",
            "dt": "Sales Invoice",
            "enabled": 1,
            "module": "Trade In",
            "name": "Trade In Child Table",
            "script": """// Parent Doctype: Sales Invoice
frappe.ui.form.on('Sales Invoice', {
    custom_is_trade_in: function(frm) {
        if (frm.doc.custom_is_trade_in) {
            // Check if "Trade In" item is already added
            const exists = frm.doc.items.some(item => item.item_code === "Trade In");
            if (!exists) {
                // Fetch the company's custom_trade_in_control_account
                frappe.db.get_value('Company', frm.doc.company, 'custom_trade_in_control_account', (data) => {
                    const incomeAccount = data.custom_trade_in_control_account || "Default Income Account"; // Provide a default if not set
                    
                    // Add a new row with "Trade In"
                    let row = frm.add_child('items', { 
                        item_code: "Trade In",
                        item_name: "Trade In",
                        income_account: incomeAccount, // Set income account dynamically
                        uom: "Nos", // Set unit of measure
                        qty: 1, // Set quantity to 1
                        description: "Trade-In" // Set description
                    });
                    frm.refresh_field('items');
                });
                frm.fields_dict.items.grid.update_docfield_property('rate', 'read_only', 1);
                frm.fields_dict.items.grid.update_docfield_property('price_list_rate', 'read_only', 1);
                frm.fields_dict.items.grid.update_docfield_property('posa_special_discount', 'read_only', 1);
                frm.fields_dict.items.grid.update_docfield_property('posa_special_rate', 'read_only', 1);
            }
        } else {
            // Confirm before removing "Trade In"
            frappe.confirm(
                'Are you sure you want to remove the "Trade In" item?',
                () => {
                    // Remove the "Trade In" item if exists
                    frm.doc.items = frm.doc.items.filter(item => item.item_code !== "Trade In");
                    frm.refresh_field('items');
                },
                () => {
                    // Re-check the checkbox if user cancels
                    frm.set_value('custom_is_trade_in', 1);
                }
            );
        }
    },

    onload: function(frm) {
        set_trade_in_fields_readonly(frm);
    },

    refresh: function(frm) {
        set_trade_in_fields_readonly(frm);
    }
});

// Child Table: Items
frappe.ui.form.on('Sales Invoice Item', {
    custom_trade_in_qty: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        calculate_row_trade_in_value(frm, cdt, cdn);
    },
    custom_trade_in_item: function(frm, cdt, cdn) {
        // Reset serial numbers when item changes
        frappe.model.set_value(cdt, cdn, 'custom_trade_in_serial_no', '');
    },
    custom_trade_in_incoming_rate: function(frm, cdt, cdn) {
        calculate_row_trade_in_value(frm, cdt, cdn);
    },
    item_code: function(frm, cdt, cdn) {
        set_item_fields_editable(frm, cdt, cdn);
    },
    onload: function(frm, cdt, cdn) {
        set_trade_in_fields_readonly(frm, cdt, cdn);
    }
});

// Calculate custom_total_trade_in_value for a specific row in the items child table
function calculate_row_trade_in_value(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // Calculate custom_total_trade_in_value as custom_trade_in_qty * custom_trade_in_incoming_rate
    let total_value = (row.custom_trade_in_qty || 0) * (row.custom_trade_in_incoming_rate || 0);
    frappe.model.set_value(cdt, cdn, 'custom_total_trade_in_value', total_value);

    // Set rate field as negative
    frappe.model.set_value(cdt, cdn, 'rate', total_value * -1); // Set rate to negative value
}

// Function to set trade-in fields read-only based on conditions
function set_trade_in_fields_readonly(frm) {
    frm.doc.items.forEach((row) => {
        // Access the specific field in the child table
        var dfItemCode = frappe.meta.get_docfield("Sales Invoice Item", "item_code", row.name);
        var dfItemName = frappe.meta.get_docfield("Sales Invoice Item", "item_name", row.name);
        var dfRate = frappe.meta.get_docfield("Sales Invoice Item", "rate", row.name);
        var dfDiscount = frappe.meta.get_docfield("Sales Invoice Item", "posa_special_discount", row.name);
        var dfSpecialRate = frappe.meta.get_docfield("Sales Invoice Item", "posa_special_rate", row.name);

        if (row.item_code === "Trade In") {
                frm.fields_dict.items.grid.update_docfield_property('rate', 'read_only', 1);
                 frm.fields_dict.items.grid.update_docfield_property('price_list_rate', 'read_only', 1);
                frm.fields_dict.items.grid.update_docfield_property('posa_special_discount', 'read_only', 1);
                frm.fields_dict.items.grid.update_docfield_property('posa_special_rate', 'read_only', 1);
            // Make fields read-only for Trade In items
            dfItemCode.read_only = 1;        // Set item_code to read-only
            dfItemName.read_only = 1;        // Set item_name to read-only
            dfRate.read_only = 1;            // Set rate to read-only
            dfDiscount.read_only = 1;        // Set posa_special_discount to read-only
            dfSpecialRate.read_only = 1;     // Set posa_special_rate to read-only
        } else {
            // If not Trade In, make fields editable
            dfItemCode.read_only = 0;        // Make item_code editable
            dfItemName.read_only = 0;        // Make item_name editable
            dfRate.read_only = 0;            // Make rate editable
            dfDiscount.read_only = 0;        // Make posa_special_discount editable
            dfSpecialRate.read_only = 0;     // Make posa_special_rate editable
        }
    });

    // Refresh the child table to reflect changes
    frm.refresh_field('items');
}

// Function to set fields editable based on item code
function set_item_fields_editable(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // Call to set fields read-only if item code is Trade In
    if (row.item_code === "Trade In") {
        set_trade_in_fields_readonly(frm);
    } else {
        // Make fields editable for the current row
        var df = frappe.meta.get_docfield("Sales Invoice Item", "item_code", row.name);
        df.read_only = 0;

        var dfRate = frappe.meta.get_docfield("Sales Invoice Item", "rate", row.name);
        dfRate.read_only = 0;

        var dfDiscount = frappe.meta.get_docfield("Sales Invoice Item", "posa_special_discount", row.name);
        dfDiscount.read_only = 0;

        var dfSpecialRate = frappe.meta.get_docfield("Sales Invoice Item", "posa_special_rate", row.name);
        dfSpecialRate.read_only = 0; // Make posa_special_rate editable

        // Refresh fields to reflect changes
        frm.refresh_field('items');
    }
}
"""
        })
        doc.insert()
        frappe.db.commit()  # Save changes
        frappe.msgprint("Client Script 'Trade In Child Table' created successfully.")
    else:
        frappe.msgprint("Client Script 'Trade In Child Table' already exists.")
