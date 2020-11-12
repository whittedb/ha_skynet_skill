from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import (UnicodeAttribute, NumberAttribute)
import settings


class AwsTellMeTable(PynamoModel):
    class Meta:
        table_name = "TellMe"
        if settings.AWS_LAMBDA_FUNCTION_NAME is None:
            if settings.AWS_HOST:
                host = settings.AWS_HOST
            if settings.AWS_REGION:
                region = settings.AWS_REGION
            if settings.AWS_ACCESS_KEY_ID:
                aws_access_key_id = settings.AWS_ACCESS_KEY_ID
            if settings.AWS_SECRET_ACCESS_KEY:
                aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        read_capacity_units = 5
        write_capacity_units = 5

    _id = UnicodeAttribute(hash_key=True)
    location = UnicodeAttribute()
    sensor_type = UnicodeAttribute()
    value = UnicodeAttribute()
    unit = UnicodeAttribute(null=True)
    name = UnicodeAttribute()
    year = NumberAttribute()
    month = NumberAttribute()
    day = NumberAttribute()
    hour = NumberAttribute()
    minute = NumberAttribute()
    second = NumberAttribute()
    microsecond = NumberAttribute()
