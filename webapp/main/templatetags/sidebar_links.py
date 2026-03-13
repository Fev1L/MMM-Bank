from django import template

register = template.Library()

@register.simple_tag
def get_links():
    return [{
        'name': 'Summary',
        'href': '/',
        'icon': 'fa-regular fa-list-check',
    },{
        'name': 'Transfer',
        'href': '/transfer',
        'icon': 'fa-regular fa-right-left',
    }, {
        'name': 'Credits',
        'href': '/credits/',
        'icon': 'fa-solid fa-landmark',
    }, {
        'name': 'Deposits',
        'href': '/deposits/',
        'icon': 'fa-solid fa-piggy-bank',
    },{
        'name': 'History',
        'href': '/history',
        'icon': 'fa-regular fa-chart-pie',
    },{
        'name': 'Account',
        'href': '/profile',
        'icon': 'fa-solid fa-user',
    },{
        'name': 'More',
        'href': '/more/',
        'icon': 'fa-ellipsis',
    }]
    