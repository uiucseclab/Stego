# Stego
#
# TO RUN:
# maxlen: python3 stego.py maxlen
# encode: python3 stego.py e "secret message here"
# decode: python3 stego.py d

import matplotlib._png as mpng
import numpy as np 
import png

import sys
import os

# SPACING must be an integer >= 1
# Default: 5
SPACING = 5

def tiles(h, w):
	"""Given the height and width of an image, returns list of tuples.
	Each tuple has the coordinates of a non-overlapping tile in 
	the image that can encode a byte (char). 
	Tile spacing is determined by SPACING.
	"""
	tile_list = []
	for i in range(0, h-1, 2*SPACING):
		for j in range(0, w-7, 8*SPACING):
			tile_list.append( (i,j) )
	return tile_list

def max_length():
	"""Returns max. length message that can be encoded based on
	PNGs in pool/ and SPACING.
	"""
	pool_list = ["pool/" + f for f in os.listdir("pool/") if '.png' in f]
	
	max_chars = 0
	for pool_im_name in pool_list:
		pool_im = mpng.read_png_int( pool_im_name )
		max_chars += len( tiles( pool_im.shape[0], pool_im.shape[1] ) )

	return max_chars


def encode_int(pool_im, coord, cint):
	"""Helper function that encodes uint8 cint within 8*2rows 
	pixels in pool_im starting at pixel at coord.
	"""
	bin_cint = bin(cint)[2:]
	while len(bin_cint) < 8:
		bin_cint = '0' + bin_cint

	for i in range(8):
		if pool_im[ coord[0]+1, coord[1]+i, 0 ] == 255:
			pool_im[ coord[0]+1, coord[1]+i, 0 ] = 254

		pool_im[ coord[0], coord[1]+i, : ] = pool_im[ coord[0]+1, coord[1]+i, : ]
		pool_im[ coord[0], coord[1]+i, 0 ] = pool_im[ coord[0]+1, coord[1]+i, 0 ] + np.uint8(bin_cint[i])

def decode_int(pool_im, coord):
	"""Helper function that returns uint8 that was encoded
	in pool_im tile starting at pixel at coord.
	"""
	bin_cint = ''
	for i in range(8):
		bin_cint += str(pool_im[ coord[0], coord[1]+i, 0 ] - pool_im[ coord[0]+1, coord[1]+i, 0 ])
	return int(bin_cint, 2)


def encode(message): 
	"""Encode the message string into images based on PNGs in pool/, 
	and store the resulting images in encoded/.
	"""
	if len(message) == 0:
		return

	pool_list = ["pool/" + f for f in os.listdir("pool/") if '.png' in f]
	assert len(message) <= max_length()

	int_list = [ ord(c) for c in message ] + [0]

	for i in range( len(pool_list) ):
		pool_im = mpng.read_png_int( pool_list[i] )

		assert pool_im.shape[2] == 3 #check if RGB image

		# print(len(tiles(pool_im.shape[0], pool_im.shape[1])), (pool_im.shape[0]//2) * (pool_im.shape[1]//8))
		for tile in tiles(pool_im.shape[0], pool_im.shape[1]):
			encode_int( pool_im, tile, int_list.pop(0) )

			if len(int_list) == 0:
				break


		png.from_array(pool_im, mode='RGB').save( "encoded/image_{0}.png".format(i) )

		if len(int_list) <= 1:
			break

	return

def decode():
	"""Decode message from PNGs in encoded/.
	Returns the decoded message string.
	"""
	number_encoded_images = len([f for f in os.listdir("encoded/") if '.png' in f])
	decoded_ints = []

	for i in range(number_encoded_images):
		encoded_im = mpng.read_png_int("encoded/image_{0}.png".format(i))
		
		for tile in tiles(encoded_im.shape[0], encoded_im.shape[1]):
			decoded_int = decode_int(encoded_im, tile)
			if decoded_int == 0:
				return ''.join([chr(c) for c in decoded_ints])

			decoded_ints.append(decoded_int)

	return ''.join([chr(c) for c in decoded_ints])


#### main ####	

# print(sys.argv)

if sys.argv[1] == 'maxlen':
	print( "Maximum message length for SPACING={0}: {1} characters".format(SPACING, max_length()) )

elif sys.argv[1] == 'e':
	message = sys.argv[2]

	if os.path.isdir("encoded/"):
		[os.remove("encoded/" + f) for f in os.listdir("encoded/") if '.png' in f]
	else:
		os.mkdir("encoded/")

	encode(message)

elif sys.argv[1] == 'd':
	print(decode())