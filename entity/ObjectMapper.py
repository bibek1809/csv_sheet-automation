class ObjectMapper:

    def map_to(self, json_data, cls):
        # return cls.from_json(request.json)
        return cls(**json_data)

    def to_json(self, cls):
        pass
