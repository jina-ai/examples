#!/bin/sh
DATA_DIR=data
mkdir -p ${DATA_DIR}
cd ${DATA_DIR}

curl -o Beethoven_1.wav https://upload.wikimedia.org/wikipedia/commons/1/1e/Beethoven_String_Quartet_3_opening.wav
curl -o Beethoven_2.wav https://upload.wikimedia.org/wikipedia/commons/0/0a/Beethoven_Piano_Concerto_4_slow_movement%2C_bars_47-55.wav
curl -o Beethoven_3.wav https://upload.wikimedia.org/wikipedia/commons/b/ba/Beethoven_Piano_Sonata_21%2C_1st_movement%2C_bars_78-84.wav
curl -o Beethoven_4.wav https://upload.wikimedia.org/wikipedia/commons/5/58/Beethoven_Piano_Sonata_Op_109%2C_2nd_movement%2C_bars_97-112.wav
curl -o Beethoven_5.wav https://upload.wikimedia.org/wikipedia/commons/3/31/Beethoven_Piano_Sonata_Op_22%2C_2nd_movement%2C_bars_30-32.wav
curl -o Beethoven_6.wav https://upload.wikimedia.org/wikipedia/commons/e/ee/Beethoven_Piano_Sonata_Op._90%2C_first_movement_bars_110-113.wav
curl -o Beethoven_7.wav https://upload.wikimedia.org/wikipedia/commons/e/ef/Beethoven_Quartet_Op._18_No.3%2C_first_movement%2C_bars_156-162.wav
curl -o Beethoven_8.wav https://upload.wikimedia.org/wikipedia/commons/9/91/Beethoven_Sonata_in_E_flat_Op_31_No_3_opening.wav
