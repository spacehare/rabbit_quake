extends Node
class_name WAD

var entries := []
var textures := []
var id # aka "magic"

const HEADER_SIZE = 24

static func from_wad_file(path) -> WAD:
	var file = FileAccess.open(path, FileAccess.READ)
	var new_wad = WAD.new()
	new_wad.id = file.get_buffer(4).get_string_from_ascii()
	var num_entries = file.get_32()
	var dir_offset = file.get_32()

	if new_wad.id != 'WAD2':
		return

	file.seek(dir_offset)
	for _i in range(num_entries):
		var orig_cursor = file.get_position()

		# entry data
		var entry := Entry.from_lump(file.get_buffer(32))
		new_wad.entries.append(entry)

		# texture data
		file.seek(entry.offset)
		# var tex = MipTex.new().from_lump(file.get_buffer(40))
		var tex := MipTex.from_file(file, entry, orig_cursor + 32)

		new_wad.textures.append(tex)
		file.seek(orig_cursor + 32)

	return new_wad

class Entry extends Resource:
	var offset: int
	var disk_size: int
	var mem_size: int
	var entry_type: String
	var compression
	var entry_name: String

	static func from_lump(lump: PackedByteArray) -> Entry:
		var e = Entry.new()
		e.offset = lump.decode_u32(0)
		e.disk_size = lump.decode_u32(4)
		e.mem_size = lump.decode_u32(8)
		e.entry_type = char(lump.decode_s8(12))
		e.compression = lump.decode_s8(14)
		e.entry_name = lump.slice(16).get_string_from_ascii()

		# "entry_type" can be 4 possible chars:
		# @ = palette
		# B = status bar
		# D = miptex
		# E = console picture
		# we want it to be D

		return e

class MipMap extends Resource:
	var width: int
	var height: int
	var data: PackedByteArray

	func to_image():
		var bytes = PackedByteArray()
		for index in data:
			var rgb = Palette.QUAKE_RGB[index]
			bytes.append(rgb[0])
			bytes.append(rgb[1])
			bytes.append(rgb[2])
			bytes.append(255 if index != 255 else 0) # TODO: make this only happen on { prefix

		var img = Image.create_from_data(width, height, false, Image.FORMAT_RGBA8, bytes)

		return img

	func to_image_texture() -> ImageTexture:
		return ImageTexture.create_from_image(to_image())

	# func to_image() -> Image:
	# 	print(data)
	# 	var i = Image.create_from_data(width, height, false, Image.FORMAT_RGBA8)
	# 	# Image.create().pix
	# 	return i

class MipTex extends Resource:
	# width and height should be divisble by 16
	var width: int:
		get:
			return mipmaps[0].width
	var height: int:
		get:
			return mipmaps[0].height
	var texture_name: String: # max 16 characters
		set(val):
			if len(val) <= 16:
				texture_name = val
	var mipmap_offsets: Array[int] = []
	var mipmaps: Array[MipMap] = [] # max 4, each mipmap is half size of the one before it

	static func from_file(file: FileAccess, entry: Entry, pos: int) -> MipTex:
		var mt = MipTex.new()

		mt.texture_name = file.get_buffer(16).get_string_from_ascii()
		var w := file.get_32()
		var h := file.get_32()

		for i in range(4):
			mt.mipmap_offsets.append(file.get_32())

		for i in range(4):
			# this godot-tools version fucking breaks formatting when doing 4 ** i to 4 * * i so pow() for now...
			file.seek(entry.offset + mt.mipmap_offsets[i])
			var mipsize = (w * h) / pow(4, i)
			var mm := MipMap.new()

			mm.data = file.get_buffer(mipsize)
			mm.width = w / pow(2, i)
			mm.height = h / pow(2, i)

			mt.mipmaps.append(mm)

		return mt
