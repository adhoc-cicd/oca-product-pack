/** @odoo-module **/

import {SaleOrderLineListRenderer} from "@sale/js/sale_order_line_field/sale_order_line_field";
import {registry} from "@web/core/registry";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineListRenderer.prototype, {
    isPackVisualHeader(record) {
        return Boolean(record.data.pack_is_visual_header);
    },

    getVisualHeaderRecords(record) {
        const records = this.props.list.records;
        const startIndex = records.indexOf(record);
        if (startIndex < 0) {
            return [];
        }
        const relatedRecords = [];
        for (let index = startIndex + 1; index < records.length; index++) {
            const line = records[index];
            if (
                line.data.display_type === "line_section" ||
                line.data.pack_is_visual_header
            ) {
                break;
            }
            relatedRecords.push(line);
        }
        return relatedRecords;
    },

    getRowClass(record) {
        const classNames = super.getRowClass(record);
        return `${classNames} ${this.isPackVisualHeader(record) ? "o_is_line_section o_is_line_section_no_indent" : ""}`;
    },

    getFormattedValue(column, record) {
        if (this.isPackVisualHeader(record) && column.name === "price_subtotal") {
            const total = this.getVisualHeaderRecords(record).reduce((sum, line) => {
                if (line.data.display_type || line.data.pack_is_visual_header) {
                    return sum;
                }
                return sum + (line.data.price_subtotal || 0);
            }, 0);
            const formatter = registry
                .category("formatters")
                .get(column.fieldType, (value) => value);
            return formatter(total, {
                ...formatter.extractOptions?.(column),
                data: record.data,
                field: record.fields[column.name],
            });
        }
        return super.getFormattedValue(column, record);
    },
});
