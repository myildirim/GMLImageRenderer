#!/usr/bin/env ruby
# Use our fetched tag data to generate images using GMLImageRenderer.py
# requires the 'curb' gem, which depends on the libcurl-dev package

require 'yaml'
require 'benchmark'
require 'rubygems'
require 'curb'

prod = true
file = ARGV[1] || "output.png"

# Parse data compiled by fetch_ga_tags.rb
ids = YAML.load(File.open('ids.yml').read)
STDOUT.puts "000000book Thumbnail Uploader -- #{ids.length} tag ids loaded."

ids.each do |id|
  file = "output#{id}.png"

  # Don't clobber existing files unless CLOBBER=1
  if File.exists?(file) && ENV['CLOBBER'].nil?
    puts "* #{id}: Output file #{file.inspect} exists already, skipping"
    next
  end

  # Shell out to python to do the work
  STDOUT.print "* #{id}: Generating #{file.inspect}... "; STDOUT.flush
  time = Benchmark.realtime { `python GMLImageRenderer.py -id #{id} #{file}` }
  STDOUT.print "#{(time*1000).round}ms. "; STDOUT.flush

  # If no file exists, something bad happened
  if !File.exists?(file)
    STDERR.puts "ERROR, failed to generate tag #{id}"
    next
  end

  # Upload via POST w/ 'image' field
  hostname = prod ? '000000book.com' : 'localhost:3000'
  STDOUT.print "\tUploading to #{hostname}... "; STDOUT.flush
  c = Curl::Easy.new("http://#{hostname}/data/#{id}/thumbnail")
  c.multipart_form_post = true
  post_field = Curl::PostField.content('image', File.open(file).read)
  post_field.remote_file = file
  post_field.content_type = 'application/octet-stream'
  time = Benchmark.realtime { res = c.http_post(post_field) }
  STDOUT.puts "HTTP #{c.response_code}, #{c.body_str.inspect} ... #{(time*1000).round}ms"
end

STDOUT.puts "Done."
exit 0
