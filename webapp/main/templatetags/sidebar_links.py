from django import template

register = template.Library()

@register.simple_tag
def get_links():
    return [{
        'name': 'Summary',
        'href': '/',
        'icon': 'fa-regular fa-list-check',
    },{
        'name': 'Credits',
        'href': '/credits/',
        'icon': 'fa-chart-pie',
    }, {
        'name': 'Deposits',
        'href': '/deposits/',
        'icon': 'fa-money-bill-1',
    }, {
        'name': 'More',
        'href': '/more/',
        'icon': 'fa-ellipsis',
    }]
    