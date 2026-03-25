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
        'href': '/contacts/',
        'icon': 'fa-regular fa-right-left',
    }, {
        'name': 'Credits',
        'href': '/credits/',
        'icon': 'fa-solid fa-chart-pie',
    }, {
        'name': 'Deposits',
        'href': '/deposits/',
        'icon': 'fa-solid fa-piggy-bank',
    },{
        'name': 'History',
        'href': '/history',
        'icon': 'fa-regular fa-landmark',
    },{
        'name': 'Account',
        'href': '/profile',
        'icon': 'fa-solid fa-user',
    },{
        'name': 'More',
        'href': '/more/',
        'icon': 'fa-ellipsis',
    }]

@register.simple_tag
def get_casino_links():
    return [{
        'name': 'Home',
        'href': '/more/casino/',
        'icon': 'fa-solid fa-home',
    },{
        'name': 'Slots',
        'href': '/more/casino/slots',
        'icon': 'fa-solid fa-dice',
    }, {
        'name': 'Poker',
        'href': '#',
        'icon': 'fa-solid fa-clover',
    }, {
        'name': 'Dice',
        'href': '#',
        'icon': 'fa-solid fa-dice-d20',
    },{
        'name': 'Guess',
        'href': '#',
        'icon': 'fa-solid fa-bullseye',
    },{
        'name': 'Roulette',
        'href': '#',
        'icon': 'fa-solid fa-circle',
    },{
        'name': 'Back',
        'href': '/more/',
        'icon': 'fa-solid fa-landmark',
    }]