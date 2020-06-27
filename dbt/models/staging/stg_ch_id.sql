select channelname as channel_name,
       cast (mediapackageid as bigint) as channel_abbreviation
from {{ source('source', 'ch_id') }}
