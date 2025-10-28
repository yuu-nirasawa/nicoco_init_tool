setting:
	ln -nsf ../../../GRID/grid_010_z62.stream ./data/GRID/
	ln -nsf ../../../GRID/grid_025_z63.stream ./data/GRID/
	ln -nsf ../../../GRID/grid_100_z63.stream ./data/GRID/
	ln -nsf ../../../test_data/2020 ./data/GLORYS12v1/
	ln -nsf ../../../test_data/coco_restart_2020070100.gt3 ./data/long-run/

clean:
	unlink data/GLORYS12v1/2020
	unlink data/GRID/grid_010_z62.stream
	unlink data/GRID/grid_025_z63.stream
	unlink data/GRID/grid_100_z63.stream
	unlink data/long-run/coco_restart_2020070100.gt3
	rm -rf sub/__pycache__
	rm sub/mod_interp.so
