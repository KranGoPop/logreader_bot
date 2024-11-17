def escape_html(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


def format_description(desc: list) -> list[str, str]:
    for i in range(len(desc)):
        desc[i] = escape_html(desc[i])
    short_desc = (desc[-1][:3700] + '<b>(...)</b>') if len(desc[-1]) > 3700 else desc[-1]
    
    if len(desc) == 1:
        return short_desc, short_desc
    
    if len(desc[0]) + len(desc[-1]) > 3700:
        while len(desc[0]) + len(desc[-1]) > 3700:
            if len(desc[0]) > len(desc[-1]):
                desc[0] = desc[0][:-1]
            else:
                desc[-1] = desc[-1][:-1]
        
        return short_desc, desc[0] + '<b>(...)</b>\n<b>...</b>\n' + desc[-1] + '<b>(...)</b>'

    rem_len = 3700 - len(desc[0]) - len(desc[-1])
    concat_desc = ''
    interrupted = False
    for desc_line in desc[-2:0:-1]:
        if len(desc_line + concat_desc) < rem_len:
            concat_desc = desc_line + concat_desc
        else:
            interrupted = True
            break
    if interrupted:
        desc = desc[0] + '<b>...</b>\n' + concat_desc + desc[-1]
    else:
        desc = desc[0] + concat_desc + desc[-1]
    
    return short_desc, desc