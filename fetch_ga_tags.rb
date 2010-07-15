require 'rubygems'
require 'mechanize'

agent = Mechanize.new

tag_ids = []
page = ENV['PAGE'] || 1

while true
  doc = agent.get("http://000000book.com/data.xml?app=Graffiti+Analysis+2.0%3A+DustTag&page=#{page}")
  xml = Nokogiri.parse(doc.body)
  ids = (xml/'id').map { |i| i.content.to_i } || []
  puts "page=#{page}, ids=#{ids.inspect}"
  break if ids.empty?
  tag_ids += ids
  page += 1
end

puts File.open('ids.txt', 'w+').write(tag_ids.to_yaml)
puts "done. ids="
puts tag_ids.inspect
