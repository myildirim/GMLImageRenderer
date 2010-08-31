#!/usr/bin/env ruby
# Fetch all DustTag tags from 000book and save to ids.yml
# TODO add an API endpoint to fetch all data w/o thumbnails! Not just DustTag
# dependencies: mechanize & nokogiri gems, which need the libxml2-dev package

require 'rubygems'
require 'mechanize'

agent = Mechanize.new
agent.user_agent = "000000book GMLImageRenderer cronjob"

tag_ids = []
start_page = ENV['PAGE'].nil? ? 1 : ENV['PAGE'].to_i
max_pages = ENV['MAX_PAGES'].nil? ? 1 : ENV['MAX_PAGES'].to_i  # nil = all

puts "Start page=#{start_page.inspect}, max_pages=#{max_pages}"

FileUtils.rm_f('ids.yml')
page = start_page
while true
  url = "http://000000book.com/data.xml?page=#{page}"
  # url += "&app=Graffiti+Analysis+2.0:+DustTag"
  doc = agent.get(url)
  xml = Nokogiri.parse(doc.body)
  ids = (xml/'id').map { |i| i.content.to_i } || []
  puts "page=#{page}, max_pages=#{max_pages}, page+max_pages=#{(page+max_pages).inspect} ids=#{ids.inspect}"
  break if ids.empty?
  tag_ids += ids
  page += 1
  break if (!max_pages.nil? && page >= (start_page+max_pages) )
end

puts File.open('ids.yml', 'w+').write(tag_ids.to_yaml)
puts "done. ids="
puts tag_ids.inspect
