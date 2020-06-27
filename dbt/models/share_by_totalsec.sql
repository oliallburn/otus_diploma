select 
	channel_name,
	sum(duration) as totalsek,
	sum(duration) * 100.0 / sum(sum(duration)) over () as percentage
from {{ ref('view_with_ch') }}
group by channel_name
order by totalsek desc


