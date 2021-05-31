from datetime import datetime


def _rebuild_item(item, country):
    item['created_at'] = datetime.now()
    item['updated_at'] = datetime.now()
    if isinstance(item['reported_at'], str):
        item['reported_at'] = datetime.strptime(item['reported_at'], "%b %d, %Y")
    if country is not None:
        item['country'] = country
    return item
