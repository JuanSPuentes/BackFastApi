class ResponseGenerator:
    def __init__(self, data, obj = str, additional_data=None):
        self.data = data
        self.additional_data = additional_data
        self.obj = obj
    
    def generate_response(self):
        if self.additional_data:
            return {"data": {self.obj : self.data}, "additional_data": self.additional_data}
        return {"data": { self.obj : self.data}}