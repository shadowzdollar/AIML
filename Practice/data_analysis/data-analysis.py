import re 

states = ["Alabama ", "Georgia!", "Georgia", "georgia", "FlOrIda", "southcarolina##", "West virginia?"]

def clean_strings(strings):
    result = []
    for value in strings:
        value = value.strip()
        value = re.sub("!#?", "", value)
        value = value.title()
        result.append(value)

    return result


clean_strings(states)