import django_filters

from .models import Car


class CarFilter(django_filters.FilterSet):

    min_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )

    max_price = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )

    min_year = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='gte'
    )

    max_year = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='lte'
    )

    min_mileage = django_filters.NumberFilter(
        field_name='mileage',
        lookup_expr='gte'
    )

    max_mileage = django_filters.NumberFilter(
        field_name='mileage',
        lookup_expr='lte'
    )

    brand = django_filters.CharFilter(
        field_name='model__brand__name',
        lookup_expr='icontains'
    )

    model = django_filters.CharFilter(
        field_name='model__name',
        lookup_expr='icontains'
    )

    transmission = django_filters.CharFilter(
        field_name='transmission',
        lookup_expr='iexact'
    )

    fuel_type = django_filters.CharFilter(
        field_name='fuel_type',
        lookup_expr='iexact'
    )

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact'
    )

    class Meta:
        model = Car

        fields = []