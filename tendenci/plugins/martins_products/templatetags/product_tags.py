from django.template import Node, Library, TemplateSyntaxError, Variable

from martins_products.models import Product
from base.template_tags import ListNode, parse_tag_kwargs

register = Library()


@register.inclusion_tag("martins_products/nav.html", takes_context=True)
def product_nav(context, user, product=None):
    context.update({
        "nav_object": product,
        "user": user
    })
    return context

class ListProductsNode(ListNode):
    model = Product
    perms = 'martins_products.view_product'


@register.tag
def list_products(parser, token):
    """
    Example:

    {% list_products as products_list [user=user limit=3 tags=bloop bleep q=searchterm] %}
    {% for product in products %}
        {{ product.something }}
    {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires more than 2" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-create_dt'

    return ListProductsNode(context_var, *args, **kwargs)

@register.inclusion_tag("martins_products/search-form.html", takes_context=True)
def product_search(context):
    return context
