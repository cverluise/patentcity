# Gravity variables

File |Source
---|---
[language_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)| [Mayer, T. & Zignago, S. (2011); Notes on CEPII’s distances measures : the GeoDist Database; CEPII Working Paper 2011-25](http://www.cepii.fr/CEPII/fr/bdd_modele/presentation.asp?id=6)

## Coverage

Country | Time
---|---
AFG	,	AGO	,	ALB	,	ARE	,	ARG	,	ARM	, AUS	,	AUT	,	AZE	,	BDI	,	BEL	,	BEN	, BFA	,	BGD	,	BGR	,	BHR	,	BIH	,	BLR	, BOL	,	BRA	,	BRB	,	BWA	,	CAF	,	CAN	, CHE	,	CHL	,	CHN	,	CIV	,	CMR	,	COG	, COL	,	COM	,	CPV	,	CRI	,	CUB	,	CYP	, CZE	,	DEU	,	DJI	,	DMA	,	DNK	,	DOM	, DZA	,	ECU	,	EGY	,	ESP	,	EST	,	ETH	, FIN	,	FRA	,	GAB	,	GBR	,	GEO	,	GHA	, GIN	,	GMB	,	GNB	,	GNQ	,	GRC	,	GTM	, HKG	,	HND	,	HRV	,	HTI	,	HUN	,	IDN	, IND	,	IRL	,	IRN	,	IRQ	,	ISL	,	ISR	, ITA	,	JAM	,	JOR	,	JPN	,	KAZ	,	KEN	, KGZ	,	KHM	,	KOR	,	KWT	,	LAO	,	LBN	, LBR	,	LBY	,	LCA	,	LKA	,	LSO	,	LTU	, LUX	,	LVA	,	MAR	,	MDA	,	MDG	,	MEX	, MKD	,	MLI	,	MLT	,	MMR	,	MNG	,	MOZ	, MRT	,	MUS	,	MWI	,	MYS	,	NAM	,	NER	, NGA	,	NIC	,	NLD	,	NOR	,	NPL	,	NZL	, OMN	,	PAK	,	PAN	,	PER	,	PHL	,	POL	, PRI	,	PRK	,	PRT	,	PRY	,	QAT	,	RUS	, RWA	,	SAU	,	SDN	,	SEN	,	SGP	,	SLE	, SLV	,	STP	,	SVK	,	SVN	,	SWE	,	SWZ	, SYC	,	SYR	,	TCD	,	TGO	,	THA	,	TKM	, TTO	,	TUN	,	TUR	,	TWN	,	TZA	,	UGA	, UKR	,	URY	,	USA	,	UZB	,	VEN	,	VNM	, YEM	,	ZAF	,	ZMB	,	ZWE				 | 2011

## Variables

Variable|Description    | Type
---|---|---
origin_country_code     | Country code of the origin country| `str`
destination_country_code| Country code of the destination country | `str`
comlang_ethno         | Whether the origin and destination country share a common language (officially or not) | `bool`
colony | Whether the destination country was a colony of the origin | `bool`
dist | Distance between the origin and destination country in km | `float`

