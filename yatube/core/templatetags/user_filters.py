from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(field):
    modify_text = ''
    i = 1
    for ch in field:
        if i % 2 == 0:
            modify_text += ch.upper()
        else:
            modify_text += ch.lower()
        i += 1
    return modify_text
