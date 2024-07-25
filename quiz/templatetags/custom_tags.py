from django import template
register = template.Library()

@register.simple_tag
def setvar(val=None):
  return val

@register.simple_tag(takes_context=True)
def increment(context, val=None):
  if val is not None:
    context[val]+=1

  return ""

@register.filter
def increment(val):
  return val+1

@register.simple_tag(takes_context=True)
def decrement(context, val=None):
  if val is not None:
    context[val]-=1

  return ""

@register.filter
def range(val):
  return range(val)

@register.simple_tag(takes_context=True)
def setarr(context, val):
  context[val]=[]
  return ""

@register.simple_tag(takes_context=True)
def appenddel(context, val):
  context['del_arr'].append(val);