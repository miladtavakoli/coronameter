class Fields:
    def _rebuild_before_insert(self, input_item, country=None, many=False):
        if many:
            for item in input_item:
                self._append_required_fields(item, country)
        else:
            self._append_required_fields(input_item, country)

        return input_item

    @staticmethod
    def _append_required_fields(item, country=None):
        item["created_at"] = datetime.now()
        item["updated_at"] = datetime.now()
        if item.get('reported_at') is not None and isinstance(item['reported_at'], str):
            item['reported_at'] = datetime.strptime(item['reported_at'], "%b %d, %Y")
        if country is not None:
            item['country'] = country

        return item
