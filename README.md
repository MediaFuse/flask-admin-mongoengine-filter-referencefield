# flask-admin-mongoengine-filter-referencefield


`This an alpha push, no tests , no finish but some filter works`


## How to use

* Put referenced_field_filter.py in your project

* import the `FilterConverterReferencedField` and use it for convert field of ReferencedField to filter


## List of converter

```python
from referenced_field_filter import FilterConverterReferencedField
converter = FilterConverterReferencedField()


column = < Referenced Document Field Object >
name = < String of Field Current Document Field >
reference_model = < Mongoengine ReferencedField Model  >
reference_field_name= < String of Mongoengine Docuement Referenced Field  >


converter.conv_string(...)
converter.conv_bool(...)
converter.conv_int(...)
converter.conv_float(...)
converter.conv_datetime(...)
converter.conv_reference(...)

```

See example

## Example

```python
# MyModel.py

from flask_admin.contrib.mongoengine import ModelView


class RefDoc(db.Document):
    foo = db.StringField(verbose_name="Foo")
    bar = db.IntField(verbose_name="bar")

class FirstDoc(db.Document):
    name = db.StringField(verbose_name="Name")
    refdoc = db.ReferenceField(RefDoc,verbose_name="Ref to RefDox",reverse_delete_rule="CASCADE")

class FirstDocView(ModelView):
  # ...
  column_filters = []
  from referenced_field_filter import FilterConverterReferencedField
  # Creation of a converter
  converter = FilterConverterReferencedField()

  # Manualy Convert
  # Creation filter for RefDoc.foo (str)

  new_filters = converter.conv_string(column=RefDoc.foo,name='refdoc',reference_model=RefDoc,reference_field_name='foo')
  # Adding filters
  column_filters += new_filters

  # Creation filter for RefDoc.foo (int)
  new_filters = converter.conv_int(column=RefDoc.bar,name='refdoc',reference_model=RefDoc,reference_field_name='bar')
  # Adding filters
  column_filters += new_filters


```
