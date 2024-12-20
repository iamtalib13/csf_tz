frappe.require([
  "/assets/csf_tz/js/csfUtlis.js",
  "/assets/csf_tz/js/shortcuts.js",
]);

frappe.ui.form.on("Sales Invoice", {
  refresh: function (frm) {
    const limit_uom_as_item_uom = getValue(
      "CSF TZ Settings",
      "CSF TZ Settings",
      "limit_uom_as_item_uom"
    );
    if (limit_uom_as_item_uom == 1) {
      frm.set_query("uom", "items", function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        return {
          query:
            "erpnext.accounts.doctype.pricing_rule.pricing_rule.get_item_uoms",
          filters: {
            value: row.item_code,
            apply_on: "Item Code",
          },
        };
      });
    }
    frm.trigger("set_pos");
    frm.trigger("make_sales_invoice_btn");
  },
  onload: function (frm) {
    frm.trigger("set_pos");
    if (frm.doc.document_status == "Draft") {
      if (frm.doc.is_return == "0") {
        frm.set_value("naming_series", "ACC-SINV-.YYYY.-");
      } else if (frm.doc.is_return == "1") {
        frm.set_value("naming_series", "ACC-CN-.YYYY.-");
        frm.set_value("select_print_heading", "CREDIT NOTE");
      }
    }
    // frm.trigger("update_stock");
  },
  customer: function (frm) {
    setTimeout(function () {
      if (!frm.doc.customer) {
        return;
      }
      if (!frm.doc.tax_category) {
        frappe.call({
          method: "csf_tz.custom_api.get_tax_category",
          args: {
            doc_type: frm.doc.doctype,
            company: frm.doc.company,
          },
          callback: function (r) {
            if (!r.exc) {
              frm.set_value("tax_category", r.message);
              frm.trigger("tax_category");
            }
          },
        });
      }
    }, 1000);
  },
  default_item_discount: function (frm) {
    frm.doc.items.forEach((item) => {
      frappe.model.set_value(
        item.doctype,
        item.name,
        "discount_percentage",
        frm.doc.default_item_discount
      );
    });
  },
  default_item_tax_template: function (frm) {
    frm.doc.items.forEach((item) => {
      frappe.model.set_value(
        item.doctype,
        item.name,
        "item_tax_template",
        frm.doc.default_item_tax_template
      );
    });
  },
  // update_stock: (frm) => {
  //     const warehouse_field = frappe.meta.get_docfield("Sales Invoice Item", "warehouse", frm.doc.name);
  //     const item_field = frappe.meta.get_docfield("Sales Invoice Item", "item_code", frm.doc.name);
  //     const qty_field = frappe.meta.get_docfield("Sales Invoice Item", "qty", frm.doc.name);
  //     if (frm.doc.update_stock){
  //         warehouse_field.in_list_view = 1;
  //         warehouse_field.idx = 3;
  //         warehouse_field.columns = 2;
  //         item_field.columns =3;
  //         qty_field.columns =1;
  //         refresh_field("items");
  //     }else{
  //         warehouse_field.in_list_view = 0;
  //         warehouse_field.columns = 0;
  //         item_field.columns =4;
  //         qty_field.columns =2;
  //         refresh_field("items");
  //     }
  // },
  make_sales_invoice_btn: function (frm) {
    if (
      frm.doc.docstatus == 1 &&
      frm.doc.enabled_auto_create_delivery_notes == 1
    ) {
      frm.add_custom_button(
        __("Create Delivery Note"),

        function () {
          frappe.call({
            method: "csf_tz.custom_api.create_delivery_note",
            args: {
              doc_name: frm.doc.name,
              method: 1,
            },
          });
        }
      );
    }
  },
  set_pos: function (frm) {
    frappe.db
      .get_value("CSF TZ Settings", {}, "auto_pos_for_role")
      .then((r) => {
        if (r.message) {
          if (
            frappe.user_roles.includes(r.message.auto_pos_for_role) &&
            frm.doc.docstatus == 0 &&
            frappe.session.user != "Administrator" &&
            frm.doc.is_pos != 1
          ) {
            frm.set_value("is_pos", true);
            frm.set_df_property("is_pos", "read_only", true);
          }
        }
      });
  },
});

frappe.ui.form.on("Sales Invoice Item", {
  item_code: function (frm, cdt, cdn) {
    validate_item_remaining_qty(frm, cdt, cdn);
  },
  qty: function (frm, cdt, cdn) {
    validate_item_remaining_qty(frm, cdt, cdn);
  },
  stock_qty: function (frm, cdt, cdn) {
    validate_item_remaining_stock_qty(frm, cdt, cdn);
  },
  uom: function (frm, cdt, cdn) {
    validate_item_remaining_qty(frm, cdt, cdn);
  },
  allow_over_sell: function (frm, cdt, cdn) {
    validate_item_remaining_stock_qty(frm, cdt, cdn);
  },
  conversion_factor: function (frm, cdt, cdn) {
    validate_item_remaining_stock_qty(frm, cdt, cdn);
  },
  warehouse: function (frm, cdt, cdn) {
    validate_item_remaining_stock_qty(frm, cdt, cdn);
  },
  csf_tz_create_wtax_entry: (frm, cdt, cdn) => {
    frappe
      .call("csf_tz.custom_api.make_withholding_tax_gl_entries_for_sales", {
        doc: frm.doc,
        method: "From Front End",
      })
      .then((r) => {
        frm.refresh();
      });
  },
});

var validate_item_remaining_qty = function (frm, cdt, cdn) {
  const item_row = locals[cdt][cdn];
  if (item_row.item_code == null) {
    return;
  }
  if (item_row.allow_over_sell == 1) {
    return;
  }
  const conversion_factor = get_conversion_factor(
    item_row,
    item_row.item_code,
    item_row.uom
  );
  frappe.call({
    method: "csf_tz.custom_api.validate_item_remaining_qty",
    args: {
      item_code: item_row.item_code,
      company: frm.doc.company,
      warehouse: item_row.warehouse,
      stock_qty: item_row.qty * conversion_factor,
      so_detail: item_row.so_detail,
    },
    async: false,
  });
};

var validate_item_remaining_stock_qty = function (frm, cdt, cdn) {
  const item_row = locals[cdt][cdn];
  if (item_row.item_code == null) {
    return;
  }
  if (item_row.allow_over_sell == 1) {
    return;
  }
  frappe.call({
    method: "csf_tz.custom_api.validate_item_remaining_qty",
    args: {
      item_code: item_row.item_code,
      company: frm.doc.company,
      warehouse: item_row.warehouse,
      stock_qty: item_row.stock_qty,
    },
    async: false,
  });
};

var get_conversion_factor = function (item_row, item_code, uom) {
  if (item_code && uom) {
    let conversion_factor = 0;
    frappe.call({
      method: "erpnext.stock.get_item_details.get_conversion_factor",
      child: item_row,
      args: {
        item_code: item_code,
        uom: uom,
      },
      async: false,
      callback: function (r) {
        if (!r.exc) {
          conversion_factor = r.message.conversion_factor;
        }
      },
    });
    return conversion_factor;
  }
};

frappe.ui.keys.add_shortcut({
  shortcut: "ctrl+q",
  action: () => {
    ctrlQ("Sales Invoice Item");
  },
  page: this.page,
  description: __("Select Item Warehouse"),
  ignore_inputs: true,
});

frappe.ui.keys.add_shortcut({
  shortcut: "ctrl+i",
  action: () => {
    ctrlI("Sales Invoice Item");
  },
  page: this.page,
  description: __("Select Customer Item Price"),
  ignore_inputs: true,
});

frappe.ui.keys.add_shortcut({
  shortcut: "ctrl+u",
  action: () => {
    ctrlU("Sales Invoice Item");
  },
  page: this.page,
  description: __("Select Item Price"),
  ignore_inputs: true,
});
