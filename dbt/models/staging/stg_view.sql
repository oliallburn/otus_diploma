select 
	subjectid as subjectid,
	viewingtime as viewingtime,
	endviewingtime as endviewingtime,
	cast (mediapackageid as bigint) as channel_abbreviation,
	duration as duration
  from {{ source('source', 'resp_view') }}
