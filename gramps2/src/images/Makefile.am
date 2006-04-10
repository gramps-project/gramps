# This is the src/images level Makefile for Gramps
# $Id: Makefile.am 6057 2006-03-03 12:49:39Z loshawlos $

SUBDIRS = 
pkgdatadir = $(datadir)/@PACKAGE@/images

map_tile_images = \
	world.topo.200407.3x128x60.jpg\
	world.topo.200407.3x400x200.jpg\
	world.topo.200407.3x800x400.jpg\
	world.topo.200407.3x1600x800_tile_0_0.jpg\
	world.topo.200407.3x1600x800_tile_0_1.jpg\
	world.topo.200407.3x1600x800_tile_0_2.jpg\
	world.topo.200407.3x1600x800_tile_0_3.jpg\
	world.topo.200407.3x1600x800_tile_1_0.jpg\
	world.topo.200407.3x1600x800_tile_1_1.jpg\
	world.topo.200407.3x1600x800_tile_1_2.jpg\
	world.topo.200407.3x1600x800_tile_1_3.jpg\
	world.topo.200407.3x3200x1600_tile_0_0.jpg\
	world.topo.200407.3x3200x1600_tile_0_1.jpg\
	world.topo.200407.3x3200x1600_tile_0_2.jpg\
	world.topo.200407.3x3200x1600_tile_0_3.jpg\
	world.topo.200407.3x3200x1600_tile_0_4.jpg\
	world.topo.200407.3x3200x1600_tile_0_5.jpg\
	world.topo.200407.3x3200x1600_tile_0_6.jpg\
	world.topo.200407.3x3200x1600_tile_0_7.jpg\
	world.topo.200407.3x3200x1600_tile_1_0.jpg\
	world.topo.200407.3x3200x1600_tile_1_1.jpg\
	world.topo.200407.3x3200x1600_tile_1_2.jpg\
	world.topo.200407.3x3200x1600_tile_1_3.jpg\
	world.topo.200407.3x3200x1600_tile_1_4.jpg\
	world.topo.200407.3x3200x1600_tile_1_5.jpg\
	world.topo.200407.3x3200x1600_tile_1_6.jpg\
	world.topo.200407.3x3200x1600_tile_1_7.jpg\
	world.topo.200407.3x3200x1600_tile_2_0.jpg\
	world.topo.200407.3x3200x1600_tile_2_1.jpg\
	world.topo.200407.3x3200x1600_tile_2_2.jpg\
	world.topo.200407.3x3200x1600_tile_2_3.jpg\
	world.topo.200407.3x3200x1600_tile_2_4.jpg\
	world.topo.200407.3x3200x1600_tile_2_5.jpg\
	world.topo.200407.3x3200x1600_tile_2_6.jpg\
	world.topo.200407.3x3200x1600_tile_2_7.jpg\
	world.topo.200407.3x3200x1600_tile_3_0.jpg\
	world.topo.200407.3x3200x1600_tile_3_1.jpg\
	world.topo.200407.3x3200x1600_tile_3_2.jpg\
	world.topo.200407.3x3200x1600_tile_3_3.jpg\
	world.topo.200407.3x3200x1600_tile_3_4.jpg\
	world.topo.200407.3x3200x1600_tile_3_5.jpg\
	world.topo.200407.3x3200x1600_tile_3_6.jpg\
	world.topo.200407.3x3200x1600_tile_3_7.jpg

dist_pkgdata_DATA = \
	bad.png\
	caution.png\
	edit_sm.png\
	events.png\
	flist.svg\
	good.png\
	gramps.png\
	locked.png\
	logo.png\
	media.svg\
	ped24.png\
	person.svg\
	place.png\
	place24.png\
	relation.svg\
	repos.png\
	repos24.png\
	sources.png\
	sources24.png\
	splash.jpg\
	stock_link.png\
	stock_lock-open.png\
	stock_lock.png\
	tools.png\
	somerights20.gif \
	document.png\
	$(map_tile_images)

EXTRA_DIST = gramps.svg 

CLEANFILES = $(map_tile_images)\
	world.topo.200407.3x1600x800.jpg\
	world.topo.200407.3x3200x1600.jpg\
	world.topo.200407.3x5400x2700.jpg

world.topo.200407%: mk_blue_marble.py
	python mk_blue_marble.py
