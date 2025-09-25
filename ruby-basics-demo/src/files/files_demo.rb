# Ruby文件操作演示模块
# 展示Ruby的文件读写、目录操作等I/O功能

class FilesDemo
  def self.demonstrate_file_operations
    puts "=== Ruby文件操作演示 ===\n".colorize(:blue)
    
    # 创建示例文件
    filename = 'data/example.txt'
    
    puts "1. 写入文件:".colorize(:yellow)
    begin
      File.open(filename, 'w') do |file|
        file.puts "Hello, Ruby!"
        file.puts "这是第二行"
        file.puts "文件操作演示"
      end
      puts "  文件已创建: #{filename}".colorize(:green)
    rescue => e
      puts "  创建文件失败: #{e.message}".colorize(:red)
    end
    
    puts "\n2. 读取文件:".colorize(:yellow)
    if File.exist?(filename)
      content = File.read(filename)
      puts "  文件内容:\n#{content}".colorize(:green)
    else
      puts "  文件不存在".colorize(:red)
    end
    
    puts "\n3. 逐行读取:".colorize(:yellow)
    if File.exist?(filename)
      File.foreach(filename).with_index do |line, index|
        puts "  第#{index + 1}行: #{line.chomp}".colorize(:green)
      end
    end
  end
  
  def self.demonstrate_directory_operations
    puts "\n=== Ruby目录操作演示 ===\n".colorize(:blue)
    
    puts "1. 当前目录:".colorize(:yellow)
    puts "  #{Dir.pwd}".colorize(:green)
    
    puts "\n2. 列出文件:".colorize(:yellow)
    Dir.glob('src/**/*.rb').first(5).each do |file|
      puts "  #{file}".colorize(:green)
    end
  end
  
  def self.run_all_demos
    demonstrate_file_operations
    demonstrate_directory_operations
  end
end