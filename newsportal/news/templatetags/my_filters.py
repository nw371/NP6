from django import template

register = template.Library()  # если мы не зарегистрируем наши фильтры, то Django никогда не узнает, где именно их искать и фильтры потеряются

@register.filter(name='censor')  # регистрируем наш фильтр под именем censor, чтоб django понимал, что это именно фильтр, а не простая функция

def censor(value):  # первый аргумент здесь это то значение, к которому надо применить фильтр, второй аргумент — это аргумент фильтра, т. е. примерно следующее будет в шаблоне value|multiply:arg
    cens_filt = ['блять', 'бля']

    text_to_check = value

    for idx, i in enumerate(cens_filt):

        text_to_check = text_to_check.replace(i,'ТУТ БЫЛ МАТ')

    return text_to_check




