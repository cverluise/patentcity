# ANNOTATION GUIDELINES


## Preliminary comments

The patent corpus we consider for East Germany (the German Democratic Republic) has 2 format categories and spans the period 1950-1992.


### *Format 1*, from to DD1 to DD123499.

This format spans the period 1951-1976.

#### Information display

The document has a header with its publication number ("*Patentschrift Nr*").
The assignee is referred to as "*Inhaber*" while the inventor is referred to as "*Erfinder*". When the same person is both the assignee and the inventor, he might referred to as "*Erfinder zugleich Inhaber*".

Well often, a geographical indication is given with the name of the assignee or the inventor. Typically, this is the name of a city (*e.g* Leipzig). It can be followed by the name of the country (especially when the latter is not Germany). The name of the city is not always given though (*cf* DD79836).

Within this format, some minor changes occur over time.
For instance, the specifically German technological class is reported up until patent DD117152, after which only the international class (IPC) is reported on the document.
Some patents will have a body of text in their first page, while others don't, but information we are interested in will always be in the header.

#### Information extraction

We extract 4 different "entities" from the header of DD patents in format category 1.

Entity|Content|E.g
---|---|---
`ASG`| Assignee full name | Inhaber: <font style="border:2px solid blue">Rhône Poulenc S.A`ASG`</font>, Paris (Frankreich).
`INV`| Inventor full name (*Erfinder*) | Erfinder: Dr. <font style="border:2px solid red">Karl Jellinek`INV`</font>, WD
`LOC`| Location of the assignee/inventor| Erfinder: Jean Auguste Phelisse, <font style="border:2px solid green">Lyon (Frankreich)`LOC`</font>.
`OCC`| Occupation of the assignee/inventor (academic title) | <font style="border:2px solid magenta">Dr.`OCC`</font> Elisabeth Kob, WD.


These entities are tied together with 2 types of relations.

| Relation     | Content                          | E.g.                                                         |
| ------------ | -------------------------------- | ------------------------------------------------------------ |
| `LOCATION`   | Links an `ASG`/`INV` to a `LOC`  | <font style="border:2px solid blue"> Rhône Poulenc S.A `ASG`</font><font color = "blue">--></font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">Paris (Frankreich)`LOC`</font> |
| `OCCUPATION` | Links an `ASG`/`INV` to an `OCC` | <font style="border:2px solid magenta">Dr `OCC`</font><font color = "magenta"><--</font>`OCCUPATION`<font color = "blue"><--</font><font style="border:2px solid blue">Elisabeth Kob `ASG`</font> |


### *Format 2*, from DD123500 onwards.

#### Information display

In this new format, relevant information are given in slots associated with a number.

For instance, the number 51 announces the (CPC) international technological class of the invention. The number 54 gives the
title of the invention.

The number 72 announces information about the inventor: identity and geographical information. The number 44 indicates the publication date.

The number 71 announces the applicant/assignee but sometimes refers to another slot to signal that this particular slot already contains the name of the applicant (*e.g*, DD126868, DD126858). In particular, a foreign assignee is more likely to be reported in line 73. Line 74 contains the name (and well often, the location) of the legal representative, which we do not tag.

#### Information extraction

We extract 4 different "entities" from the header of DD patents in format category 2.

Entity|Content|E.g
---|---|---
`ASG`| Assignee full name | <font style="border:2px solid blue">Maschinenfabrik Köppern GmbH & Co KG`ASG`</font>, Hattingen, DE
`INV`| Inventor full name (*Erfinder*) | (72) <font style="border:2px solid red">Bergendahl, Hans-Georg `INV`</font>, DE
`LOC`| Location of the assignee/inventor| Knieling, Norbert, Dipl-Phys., <font style="border:2px solid green">12439 Berlin, DE`LOC`</font>.
`OCC`| Occupation of the assignee/inventor (academic title) | Knieling, Norbert, <font style="border:2px solid magenta">Dipl-Phys.`OCC`</font>, 12439 Berlin, DE.

These entities are tied together with 2 types of relations.


| Relation     | Content                          | E.g.                                                         |
| ------------ | -------------------------------- | ------------------------------------------------------------ |
| `LOCATION`   | Links an `ASG`/`INV` to a `LOC`  | <font style="border:2px solid blue"> Maschinenfabrik Köppern GmbH & Co KG `ASG`</font><font color = "blue">--></font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green"> Hattingen, DE `LOC`</font> |
| `OCCUPATION` | Links an `ASG`/`INV` to an `OCC` | <font style="border:2px solid blue"> Lämmer, Hans-Georg `ASG`</font><font color = "blue">--></font>`LOCATION`<font color = "magenta">--></font><font style="border:2px solid magenta">Dipl-Ing. `OCC`</font> |


## Entities

### Format 1

#### The tag `INV`

The tag `INV` refers to the full name of an inventor. This is a person that is not referred to as the assignee and is specifically referred to as the inventor (*Erfinder*).

##### Specific cases
- *Inventor only*: some early patents report an inventor but no assignee. We tag the inventor as it is mentioned nonetheless. See example 2.
- *Secret inventor*: in some patents, it is specifically mentioned  that the inventor remains anonymous. In this case, we do not tag anything. See example 3.
- *Inventor=Assignee*: sometimes, the inventor and the assignee are the same person and the document won't repeat the name; this may be signalled by the phrase "*Erfinder zugleich Inhaber*". In this case, we tag the name only as the inventor, because a single group of words cannot be tagged twice. See example 4.

##### Examples

**Example 1: *Standard Case* with a person, from patent DD79836**
> Erfinder: <font style="border:2px solid red">Wilhelm Uhrig`INV`</font>, WD


**Example 2: *Inventor only*, from patent DD5076**
> Erfinder: Dr <font style="border:2px solid red">ALEXANDER PRANSCHKE`INV`</font>, Schwarzheide.
Dr <font style="border:2px solid red">ERWIN SAUTER`INV`</font>, Schwarzheide.

**Example 3: *Inventor only*, from patent DD4075**
> Erfinderbenennung ist ausgesetzt.

**Example 4: *Inventor=Assignee*, from patent DD15399**

> Erfinder zugleich Inhaber: <font style="border:2px solid red">Zalter Gleißner`INV`</font>, Weißenfeis (Saale)

#### The tag `ASG`

The tag `ASG` refers to the full name(s) of the person(s) or firm(s) who own(s) the patent rights.

##### Specific cases

- *Rechtsträger*: Some patents distinguish between *Inhaber* and *Rechtsträger*: we keep tagging the *Inhaber* person as the assignee. See example 2.

##### Examples

**Example 1: *Standard Case* with a firm, from patent DD79836**
> Inhaber: <font style="border:2px solid blue"> Dr. Plate GmbH`ASG`</font>, Bonn, WD.


**Example 2: *Rechtsträger*, from patent DD33554**

> Erfinder: Manfred Gerlach, Dresden; Kurt Jäger, Dresden; Dipl-Ing. Gerhard Kasche, Dresden.
> Inhaber: <font style="border:2px solid blue">Eigentum des Volkes`ASG`</font>; <font style="border:2px solid blue">Kurt Jäger`ASG`</font>, Dresden; Dipl-Ing. <font style="border:2px solid blue">Gerhard Kasche`ASG`</font>, Dresden.
> Rechtsträger: VEB Gasturbinenbau und Energiemaschinenentwicklung Pirna, Pirna.

#### The tag `LOC`

The tag `LOC` refers to the full location sequence of an assignee or inventor.
In some patents, no location is reported (see DD86584).


##### Specific cases

- *District*: The patents might report the district within a given city, which we tag along. See example 3.

**Example 1: *Standard Case* with a location for the (foreign) assignee and a location for the (foreign) inventor, from patent DD76817**
> Erfinder: Abraham A.Goldberg, <font style="border:2px solid green">USA`LOC`</font>.
> Inhaber: COLUMBIA BROADCASTING SYSTEM, INC., <font style="border:2px solid green">New York, USA`LOC`</font>.

**Example 2: *Standard Case* with German patentees, from patent DD69242**
> Erfinder: Dr-Ing. Walter Froede, <font style="border:2px solid green">Neckarsulm (WD)`LOC`</font>.
> Inhaber: NSU-Motorenwenke AG, <font style="border:2px solid green">Neckarsulm (WD)`LOC`</font>
> Wandel GmbH, <font style="border:2px solid green">Lindau (WD)`LOC`</font>

**Example 3: *District* from patent DD62143**
> Erfinder zugleich Inhaber: Dr. Wolfram Jenichen, <font style="border:2px solid green">Schönow (b. Berlin)`LOC`</font>.



#### The tag `OCC`

This tag concerns the university title of inventors/assignees. When none is reported, we do not tag anything.

##### Examples

**Example 1: *Standard Case* with several inventors from patent DD1393**
> Erfinder: <font style="border:2px solid magenta">Dr.`OCC`</font> GERHARD HANSEN, <font style="border:2px solid magenta">Dr`OCC`</font> PAUL HEINZ KECK, Jena.
> <font style="border:2px solid magenta">Dipl.-Ing.`OCC`</font> KARL ILMER, Jena.


### Format 2

#### The tag `INV`

The tag `INV` refers to the full name of an inventor. This is a person that is not referred to as the assignee and is specifically referred to as the inventor (*Erfinder*).

##### Specific cases
- *Secret inventor*: some publications do not report the name of the inventor on purpose. This may be signalled by the sentence "*Erfinder: werden aug Antrag nicht genannt*". See example 2.
- *Inventor=Assignee*: sometimes, the inventor and the assignee are the same person and the document won't repeat the name; this may be signalled by the phrase "*siehe (72)*" in line 71 (where the assignee should be). In this case, we tag the name only as the inventor, because a single group of words cannot be tagged twice. See example 3.

##### Examples
**Example 1: *Standard Case* with several inventors, from patent DD251362**
> (72) <font style="border:2px solid red">Kolitsch, Andreas`INV`</font>, Dr.; <font style="border:2px solid red">Richter, Edgar`INV`</font>, Dr.; <font style="border:2px solid red">Mende, Edgar`INV`</font>; <font style="border:2px solid red">Polnik, Frank`INV`</font>, DD

**Example 2: *Secret inventor*, from patent DD126770**
> Erfinder: werden aug Antrag nicht genannt

**Example 3: *Inventor=Assignee*, from patent DD148904**
> (71) siehe (72).
> (72) <font style="border:2px solid red">Trabert, Erich`INV`</font>, DD

#### The tag `ASG`

The tag `ASG` refers to the full name(s) of the person(s) or firm(s) who own(s) the patent rights.

##### Specific cases

- *Foreign Assignee*: When the assignee is non-German, it might be reported in line (73) instead of (71). See example 2.

##### Examples
**Example 1: *Standard Case* with a government-run company, from patent DD133115**
> (71) <font style="border:2px solid blue">Akademie der Wissenschaften der DDR, Zentralinstitut for Isotopen- und Strahlenforschung`ASG`</font>, Leipzig , DD

**Example 2: *Foreign Assignee*, from patent DD202259**
> (71) siehe (73)
> (73) <font style="border:2px solid blue">ITERA COMPONENTS AB`ASG`</font>, GOETEBORG, SE


#### The tag `LOC`

The tag `LOC` refers to the full location sequence of an assignee or inventor. Typically, only the country will be reported for inventors, but greater details may be given for assignees.  Here are a few abbreviations that are used throughout the patents.

- SU: Soviet Union
- HU: Hungary
- CS: Tchecoslovaquia
- BG: Bulgaria
- WD: West-Germany.

##### Specific cases

- *Full Address*: There is quite a number of Format 2 patents which report the full address of an assignee or inventor, and in this case we tag it all. See example 2.


##### Examples

**Example 1: Standard Case with the country and the city from patent DD141623**
> (71) Akademie der Wissenschaften der DDR, <font style="border:2px solid green">Berlin, DD`LOC`</font>.

**Example 2: *Full Address* from patent DD251362**
> (71) Akademie der Wissenschaften der DDR, <font style="border:2px solid green">Otto-Nuschke Straße 22/23, Berlin 1080, DD`LOC`</font>.

#### The tag `OCC`

This tag concerns the university title of inventors/assignees. When none is reported, we do not tag anything.

##### Examples

**Example 1: *Standard Case* with several inventors from patent DD220001**
> (72): Lämmer, Hans-Georg, <font style="border:2px solid magenta">Ing-Dipl.`OCC`</font>; Sommer, Peter; Matzner, Dieter, <font style="border:2px solid magenta">Dipl-Ing.`OCC`</font>, DD.

## Relationships

See [XX\_REL\_ANNOTATION\_GUIDELINES.md](./XX_REL_ANNOTATION_GUIDELINES.md).


## Examples

##### Example 1: Format 1 (DD-1300)

![Example 1: format 1](./img/DD-1300.png)

##### Example 2: Format 2 (DD-142651)

![Example 2: format 2](./img/DD-142651.png)
