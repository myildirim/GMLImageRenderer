#!/usr/bin/env ruby
# Fetch all DustTag tags from 000book and save to ids.yml
# TODO add an API endpoint to fetch all data w/o thumbnails! Not just DustTag
# dependencies: mechanize & nokogiri gems, which need the libxml2-dev package

require 'rubygems'
require 'mechanize'

agent = Mechanize.new

tag_ids = []
page = ENV['PAGE'] || 1
max_pages = ENV['MAX_PAGES'] || 5 # nil = all

FileUtils.rm_f('ids.yml')
while true
  url = "http://000000book.com/data.xml?page=#{page}"
  doc = agent.get(url)
  xml = Nokogiri.parse(doc.body)
  ids = (xml/'id').map { |i| i.content.to_i } || []
  puts "page=#{page}, ids=#{ids.inspect}"
  break if ids.empty?
  tag_ids += ids
  page += 1
  break if (!max_pages.nil? && page > max_pages)
end

puts File.open('ids.yml', 'w+').write(tag_ids.to_yaml)
puts "done. ids="
puts tag_ids.inspect
