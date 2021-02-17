from datetime import date


def cars_export_stats(total, new, sold, publish, draft, private):
    today = date.today()
    today = today.strftime("%B %d, %Y")
    text = f"Statistics of {today} export.<br><br>" \
           f"<strong>{new}<strong> new cars.<br>" \
           f"<strong>{sold}<strong> were sold.<br>"\
           f"<strong>{total}<strong> total. " \
           f"<strong>{publish}/{draft}/{private}<strong> publish/draft/private."
    return text
