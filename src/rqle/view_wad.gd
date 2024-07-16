extends Control

var p = r"I:\Quake\Dev\wad\python.wad"

@onready var wad_container: BoxContainer = %WadContainer

func _ready():
	var w := WAD.from_wad_file(p)
	var imgtex: ImageTexture = w.textures[0].mipmaps[0].to_image_texture()
	var rect = TextureRect.new()
	rect.texture = imgtex
	rect.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	rect.custom_minimum_size = Vector2(256, 256)
	rect.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	wad_container.add_child(rect)
