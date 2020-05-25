from wtforms import StringField


class StringFieldDefault(StringField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0] != '':
            self.data = valuelist[0]
        else:
            self.data = self.object_data
