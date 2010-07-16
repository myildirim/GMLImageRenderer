#!/usr/bin/ruby
require 'rubygems'
require 'curb'
require 'yaml'

prod = true
#id = ARGV[0] || 18013
file = ARGV[1] || "output.png"
#puts "uploading tag id=#{id.inspect} file=#{file.inspect}"

ids = YAML.load(File.open('ids.yml').read)
puts "#{ids.length} tag ids loaded."

ids.each do |id|
  puts "id=#{id}"
  file = "output#{id}.png"

  puts `python GMLImageRenderer.py -id #{id} #{file}`
  #puts `open #{file}`

  c = Curl::Easy.new("http://#{prod ? '000000book.com' : 'localhost:3000'}/data/#{id}/thumbnail")
  c.multipart_form_post = true
  post_field = Curl::PostField.content('image', File.open(file).read)
  post_field.remote_file = file
  post_field.content_type = 'application/octet-stream'
  res = c.http_post(post_field)
  puts res.inspect
end
puts "done"
