from odoo import http

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleVariantController(WebsiteSaleVariantController):
    @http.route(
        "/website_sale/get_combination_info",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_combination_info_website(
        self,
        product_template_id,
        product_id,
        combination,
        add_qty,
        parent_combination=None,
        **kw,
    ):
        if "context" in kw:
            kw["context"].update({"whole_pack_price": True})
        else:
            kw["context"] = {"whole_pack_price": True}
        return super().get_combination_info_website(
            product_template_id,
            product_id,
            combination,
            add_qty,
            parent_combination=parent_combination,
            **kw,
        )
