"""

Custom Filter for Filtering in ReferencedField



"""
from flask_admin.babel import lazy_gettext
from flask_admin.model import filters
from flask_admin.contrib.mongoengine.filters import BaseMongoEngineFilter

from flask_admin.contrib.mongoengine.tools import parse_like_term
from mongoengine.queryset import Q
from bson.errors import InvalidId
from bson.objectid import ObjectId

class BaseMongoEngineFilterRef(BaseMongoEngineFilter):
    def __init__(self, column, name, options=None, data_type=None, reference_model=None, reference_field_name=None):
        """
            Constructor.

            :param column:
                Model field
            :param name:
                Display name
            :param options:
                Fixed set of options. If provided, will use drop down instead of textbox.
            :param data_type:
                Client data type
            :param reference_model:
                Mongoengine Class object of pointed Referenced Field
            :param reference_field_name:
                Name of field for quering.


            Exemple

            class Client(db.Document):
                ...

            class Foo(db.Document):
                client = db.ReferenceField(Clients,verbose_name="Client")

            class FooView(ModelView):
                ...

                from referenced_field_filter import FilterConverterReferencedField
                converter = FilterConverterReferencedField()

                new_filters = converter.conv_string(column=Clients.name,name='client',referenced_model=Clients,refrenced_field_name='nomcourant')

                column_filters += new_filters

        """
        super(BaseMongoEngineFilterRef, self).__init__(name, options, data_type)
        self.name = f'{name}.{reference_field_name}'
        self.name_ori = name
        self.column = column
        self.reference_field_name = reference_field_name
        self.reference_model = reference_model

    def __unicode__(self):
        return f'{self.name}.{self.reference_field_name}'

    def clean(self, value):
        """
            Parse value into python format. Occurs before .apply()

            :param value:
                Value to parse
        """
        return value
# Common filters
class FilterEqualRef(BaseMongoEngineFilterRef):

    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori : self.reference_model.objects(**{"%s" % self.reference_field_name : value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('equals')


class FilterNotEqualRef(BaseMongoEngineFilterRef):
    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori : self.reference_model.objects(**{'%s__ne' %  self.reference_field_name: value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not equal')


class FilterLikeRef(BaseMongoEngineFilterRef):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__in' % self.name_ori : self.reference_model.objects(**{'%s__%s' %  (self.reference_field_name, term): data})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('contains')


class FilterNotLikeRef(BaseMongoEngineFilterRef):
    def apply(self, query, value):
        term, data = parse_like_term(value)
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(
            **{'%s__not__%s' % (self.reference_field_name, term): data})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not contains')


class FilterGreaterRef(BaseMongoEngineFilterRef):
    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__gt' % self.reference_field_name: value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('greater than')


class FilterSmallerRef(BaseMongoEngineFilterRef):
    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__lt' % self.reference_field_name: value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('smaller than')


class FilterEmptyRef(BaseMongoEngineFilterRef, filters.BaseBooleanFilter):
    def apply(self, query, value):
        if value == '1':
            flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s' % self.reference_field_name: None})}
        else:
            flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__ne' % self.reference_field_name: None})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('empty')


class FilterInListRef(BaseMongoEngineFilterRef):
    def __init__(self, column, name, options=None, data_type=None):
        super(FilterInListRef, self).__init__(column, name, options, data_type='select2-tags')

    def clean(self, value):
        return [v.strip() for v in value.split(',') if v.strip()]

    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__in' % self.reference_field_name: value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('in list')


class FilterNotInListRef(FilterInListRef):
    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__nin' % self.reference_field_name: value})}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('not in list')


# Customized type filters
class BooleanEqualFilter(FilterEqualRef, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s' % self.reference_field_name: value == '1'})}
        return query.filter(**flt)


class BooleanNotEqualFilter(FilterNotEqualRef, filters.BaseBooleanFilter):
    def apply(self, query, value):
        flt = {
            '%s__in' % self.name_ori: self.reference_model.objects(**{'%s' % self.reference_field_name: value != '1'})}
        return query.filter(**flt)


class IntEqualFilterRef(FilterEqualRef, filters.BaseIntFilter):
    pass


class IntNotEqualFilterRef(FilterNotEqualRef, filters.BaseIntFilter):
    pass


class IntGreaterFilterRef(FilterGreaterRef, filters.BaseIntFilter):
    pass


class IntSmallerFilterRef(FilterSmallerRef, filters.BaseIntFilter):
    pass


# class IntInListFilterRef(filters.BaseIntListFilter, FilterInListRef):
#     pass


# class IntNotInListFilterRef(filters.BaseIntListFilter, FilterNotInListRef):
#     pass


class FloatEqualFilterRef(FilterNotEqualRef, filters.BaseFloatFilter):
    pass


class FloatNotEqualFilterRef(FilterNotEqualRef, filters.BaseFloatFilter):
    pass


class FloatGreaterFilterRef(FilterGreaterRef, filters.BaseFloatFilter):
    pass


class FloatSmallerFilterRef(FilterSmallerRef, filters.BaseFloatFilter):
    pass


# class FloatInListFilterRef(filters.BaseFloatListFilter, FilterInListRef):
#     pass


# class FloatNotInListFilterRef(filters.BaseFloatListFilter, FilterNotInListRef):
#     pass


class DateTimeEqualFilterRef(FilterEqualRef, filters.BaseDateTimeFilter):
    pass


class DateTimeNotEqualFilterRef(FilterNotEqualRef, filters.BaseDateTimeFilter):
    pass


class DateTimeGreaterFilterRef(FilterGreaterRef, filters.BaseDateTimeFilter):
    pass


class DateTimeSmallerFilterRef(FilterSmallerRef, filters.BaseDateTimeFilter):
    pass


class DateTimeBetweenFilterRef(BaseMongoEngineFilterRef, filters.BaseDateTimeBetweenFilter):
    def __init__(self, column, name, options=None, data_type=None,reference_model=None, reference_field_name=None):

        super(DateTimeBetweenFilterRef, self).__init__(column,
                                                    name,
                                                    options=None,
                                                    data_type='datetimerangepicker',reference_model=None, reference_field_name=None)

        self.name = f'{name}.{reference_field_name}'
        self.name_ori = name
        self.column = column
        self.options = None
        self.reference_field_name = reference_field_name
        self.reference_model = reference_model

    def apply(self, query, value):
        start, end = value
        flt = {'%s__in' % self.name_ori: self.reference_model.objects(**{'%s__gte' % self.reference_field_name: start, '%s__lte' %self.reference_field_name : end })}

        return query.filter(**flt)


class DateTimeNotBetweenFilterRef(DateTimeBetweenFilterRef):
    def apply(self, query, value):
        start, end = value

        return query.filter(
            Q(**{'%s__in' % self.name_ori: self.reference_model.objects(
                        **{'%s__not__gte' % self.reference_field_name: start})}) |
            Q(**{'%s__in' % self.name_ori: self.reference_model.objects(
                **{'%s__not__lte' % self.reference_field_name: end})})
        )

    def operation(self):
        return lazy_gettext('not between')


class ReferenceObjectIdFilterRef(BaseMongoEngineFilterRef):
    def validate(self, value):
        """
            Validate value.
            If value is valid, returns `True` and `False` otherwise.
            :param value:
                Value to validate
        """
        try:
            self.clean(value)
            return True
        except InvalidId:
            return False

    def clean(self, value):
        return ObjectId(value.strip())

    def apply(self, query, value):
        flt = {'%s' % self.column.name: value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('ObjectId equals')


# Base MongoEngine filter field converter
class FilterConverterReferencedField(filters.BaseFilterConverter):
    #strings = (FilterLike, FilterNotLike, FilterEqual, FilterNotEqual,
    strings = (FilterEqualRef, FilterNotEqualRef, FilterLikeRef, FilterNotLikeRef)
    int_filters = (IntEqualFilterRef, IntNotEqualFilterRef, IntGreaterFilterRef,
                   IntSmallerFilterRef, FilterEmptyRef)\
        #, IntInListFilterRef,
         #          IntNotInListFilterRef)
    float_filters = (FloatEqualFilterRef, FloatNotEqualFilterRef, FloatGreaterFilterRef,
                     FloatSmallerFilterRef, FilterEmptyRef)
    #FloatInListFilterRef,
     #                FloatNotInListFilterRef)
    bool_filters = (BooleanEqualFilter, BooleanNotEqualFilter)
    datetime_filters = (DateTimeEqualFilterRef, DateTimeNotEqualFilterRef,
                        DateTimeGreaterFilterRef, DateTimeSmallerFilterRef,
                        DateTimeBetweenFilterRef, DateTimeNotBetweenFilterRef,
                        FilterEmptyRef)
    reference_filters = (ReferenceObjectIdFilterRef,)




    def convert(self, type_name, column, name):
        filter_name = type_name.lower()

        if filter_name in self.converters:
            return self.converters[filter_name](column, name)

        return None

    @filters.convert('StringField', 'EmailField', 'URLField')
    def conv_string(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.strings]

    @filters.convert('BooleanField')
    def conv_bool(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.bool_filters]

    @filters.convert('IntField', 'LongField')
    def conv_int(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.int_filters]

    @filters.convert('DecimalField', 'FloatField')
    def conv_float(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.float_filters]

    @filters.convert('DateTimeField', 'ComplexDateTimeField')
    def conv_datetime(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.datetime_filters]

    @filters.convert('ReferenceField')
    def conv_reference(self, column, name, reference_model, reference_field_name):
        return [f(column=column, name=name,reference_model=reference_model,reference_field_name=reference_field_name) for f in self.reference_filters]
