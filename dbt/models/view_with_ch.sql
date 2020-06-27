select 
	n.subjectid,
	n.viewingtime,
	n.endviewingtime,
	n.channel_abbreviation,
	n.duration,
	s.channel_name
from {{ ref('stg_view') }} n
join {{ ref('stg_ch_id') }} s
	on n.channel_abbreviation = s.channel_abbreviation
