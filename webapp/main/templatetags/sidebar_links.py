from django import template

register = template.Library()

@register.simple_tag
def get_links():
    return [{
        'name': 'Cards',
        'href': '/',
        'icon': 'fa-credit-card',
    },{
        'name': 'Credits',
        'href': '/credits',
        'icon': 'fa-chart-pie',
    }, {
        'name': 'Deposites',
        'href': '/deposites',
        'icon': 'fa-money-bill-1',
    }, {
        'name': 'More',
        'href': '../more',
        'icon': 'fa-ellipsis',
    }]
    