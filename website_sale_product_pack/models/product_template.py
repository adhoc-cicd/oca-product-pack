# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains("is_published")
    def check_website_published(self):
        """For keep the consistent and prevent bugs within the e-commerce,
        we force that all childs of a parent pack
        stay publish when the parent is published.
        Also if any of the childs of the parent pack became unpublish,
        we unpublish the parent."""
        for rec in self.filtered(lambda x: x.pack_ok and x.is_published):
            unpublished = rec.pack_line_ids.mapped("product_id").filtered(
                lambda p: not p.is_published
            )
            if unpublished:
                raise ValidationError(
                    _(
                        "You can't unpublished products (%(unpublished_products)s) to a"
                        "published pack (%(pack_name)s)"
                    )
                    % {
                        "unpublished_products": ", ".join(unpublished.mapped("name")),
                        "pack_name": rec.name,
                    }
                )

        for rec in self.filtered(
            lambda x: not x.is_published and x.used_in_pack_line_ids
        ):
            published = rec.used_in_pack_line_ids.mapped("parent_product_id").filtered(
                "is_published"
            )
            if published:
                raise ValidationError(
                    _(
                        "You can't unpublished product (%(product_name)s) for a"
                        "published pack parents (%(pack_parents)s)"
                    )
                    % {
                        "product_name": rec.name,
                        "pack_parents": ", ".join(published.mapped("name")),
                    }
                )

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        parent_combination=False,
        only_template=False,
    ):
        """Override to add the information about renting for rental products"""
        return super(
            ProductTemplate, self.with_context(whole_pack_price=True)
        )._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, date, website
    ):
        """Override to add the information about renting for rental products"""
        res = super()._get_additionnal_combination_info(
            product_or_template, quantity, date, website
        )

        if product_or_template.pack_ok:
            currency = website.currency_id
            pricelist = website.pricelist_id
            res["price"] = pricelist.with_context(
                whole_pack_price=True
            )._get_product_price(
                product=product_or_template,
                quantity=quantity,
                currency=currency,
            )

        return res

    def _get_sales_prices(self, website):
        """Override to add the price of the pack itself"""
        packs, no_packs = self.with_context(whole_pack_price=True).split_pack_products()
        prices = super(ProductTemplate, no_packs)._get_sales_prices(website)
        if packs:
            pricelist = website.pricelist_id
            for pack in packs:
                prices[pack.id] = {
                    "price_reduce": pricelist.with_context(
                        whole_pack_price=True
                    )._get_product_price(product=pack, quantity=1.0)
                }
        return prices
