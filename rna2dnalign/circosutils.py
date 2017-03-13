# -*- coding: utf-8 -*-
""" Boilerplate configuration files for circos
"""

CIRCOS_CONF = '''
<<include colors_fonts_patterns.conf>>
<<include ticks.conf>>
<<include ideogram.conf>>

<image>
<<include etc/image.conf>>
</image>

karyotype   = data/karyotype/karyotype.human.txt

chromosomes_units = 100000
chromosomes       = -hsY
chromosomes_display_default = yes

<plots>

#########     1: TPtr     #############
<plot>
type             = scatter
stroke_thickness = 1

file             = conf(sample_name)_Ttr.txt
fill_color= 209,209,117 # cream yellow
stroke_color= 209,209,117 # cream yellow
glyph            = square
glyph_size       = 5

max   = 1
min   = 0

r0    = 0.80r
r1    = 0.95r


<backgrounds>
<background>
color     =80,80,80
y0        = 0.00
</background>
</backgrounds>

<axes>
<axis>
color = 127,127,127
thickness = 1
spacing   = 0.1r
y0        = 0.006
</axis>
</axes>

</plot>

########      2: TPex     ##########


<plot>
type             = scatter
stroke_thickness = 1

file             = conf(sample_name)_Tex.txt
fill_color = 255,171,82 # orange
stroke_color= 255,171,82 # orange
glyph            = square
glyph_size       = 5

max   = 1
min   = 0
r0    = 0.63r
r1    = 0.78r


<backgrounds>
<background>
color     = 110,110,110
y0        = 0.006
</background>
</backgrounds>

<axes>
<axis>
color = 45,45,45
thickness = 1
spacing   = 0.1r
y0        = 0.006
</axis>
</axes>

</plot>


##############     3: Ntr     #############
<plot>

type             = scatter
stroke_thickness = 1

file             = conf(sample_name)_Ntr.txt
fill_color= 140,217,217 # light blue
stroke_color= 140,217,217 # light blue
glyph            = square
glyph_size       = 5

max   = 1
min   = 0

r0    = 0.46r
r1    = 0.61r


<backgrounds>
<background>
color     =80,80,80
y0        = 0.00
</background>
</backgrounds>

<axes>
<axis>
color = 127,127,127
thickness = 1
spacing   = 0.1r
y0        = 0.006
</axis>
</axes>

</plot>



########     4: NTex     ##########


<plot>

type             = scatter
stroke_thickness = 1

file             = conf(sample_name)_Nex.txt
fill_color =  83,140,198 # dark blue
stroke_color= 83,140,198 # dark blue
glyph            = square
glyph_size       = 5

max   = 1
min   = 0

r0    = 0.29r
r1    = 0.44r


<backgrounds>
<background>
color     = 110,110,110
y0        = 0.006
</background>
</backgrounds>

<axes>
<axis>
color = 45,45,45
thickness = 1
spacing   = 0.1r
y0        = 0.006
</axis>
</axes>

</plot>

</plots>

<<include etc/housekeeping.conf>>
'''

TICKS_CONF = '''
show_ticks          = yes
show_tick_labels    = yes

<ticks>

radius           = dims(ideogram,radius_outer)
orientation      = out
label_multiplier = 1e-6
color            = black
size             = 20p
thickness        = 3p
label_offset     = 5p
format           = %d

<tick>
spacing        = 75u
show_label     = no
label_size     = 10p
size           = 10p
</tick>

<tick>
spacing        = 250u
show_label     = yes
label_size     = 15p
size           = 15p
</tick>

<tick>
spacing        = 500u
show_label     = yes
label_size     = 20p
</tick>

</ticks>
'''

IDEOGRAM_CONF = '''
<ideogram>

<spacing>
default = 0.005r
break   = 0.005r
</spacing>

<<include ideogram.position.conf>>
<<include ideogram.label.conf>>
<<include bands.conf>>

radius*       = 0.85r

</ideogram>
'''

IDEOGRAM_POSITION_CONF = '''
radius           = 0.775r
thickness        = 30p
fill             = yes
fill_color       = black
stroke_thickness = 2
stroke_color     = black
'''

IDEOGRAM_LABEL_CONF = '''
show_label       = yes
label_font       = light
label_center     = yes
label_radius     = dims(image,radius)-80p
label_size       = 38
label_color      = black
label_parallel   = yes
label_case       = lower
label_format     = eval(sprintf("chr%s",var(label)))
'''

BANDS_CONF = '''
show_bands            = yes
fill_bands            = yes
band_stroke_thickness = 6
band_stroke_color     = black
band_transparency     = 0.05
'''

CONFDICT = {
    'circos.conf': CIRCOS_CONF,
    'ticks.conf': TICKS_CONF,
    'ideogram.conf': IDEOGRAM_CONF,
    'ideogram.label.conf': IDEOGRAM_LABEL_CONF,
    'ideogram.position.conf': IDEOGRAM_POSITION_CONF,
    'bands.conf': BANDS_CONF,
}
