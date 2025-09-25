# Ruby块与迭代器演示模块
# 展示Ruby的块语法、yield关键字和常用迭代器

class BlocksDemo
  def self.demonstrate_basic_blocks
    puts "=== Ruby基础块演示 ===\n".colorize(:blue)
    
    puts "1. 基本块语法:".colorize(:yellow)
    # 大括号语法
    [1, 2, 3].each { |num| puts "  数字: #{num}".colorize(:green) }
    
    # do...end语法
    puts "\n  使用do...end语法:"
    ['a', 'b', 'c'].each do |letter|
      puts "    字母: #{letter}".colorize(:green)
    end
    
    puts "\n2. 块作为参数:".colorize(:yellow)
    def greet_with_block
      puts "  开始问候..."
      yield if block_given?
      puts "  问候结束."
    end
    
    greet_with_block { puts "    Hello from block!".colorize(:green) }
    
    puts "\n3. 带参数的块:".colorize(:yellow)
    def process_numbers(*numbers)
      numbers.each { |num| yield(num, num * 2) if block_given? }
    end
    
    process_numbers(1, 2, 3) do |original, doubled|
      puts "  #{original} -> #{doubled}".colorize(:green)
    end
  end
  
  def self.demonstrate_iterators
    puts "\n=== Ruby常用迭代器演示 ===\n".colorize(:blue)
    
    data = [1, 2, 3, 4, 5]
    
    puts "1. map/collect:".colorize(:yellow)
    squared = data.map { |n| n ** 2 }
    puts "  原数组: #{data}".colorize(:cyan)
    puts "  平方后: #{squared}".colorize(:green)
    
    puts "\n2. select/filter:".colorize(:yellow)
    evens = data.select { |n| n.even? }
    puts "  偶数: #{evens}".colorize(:green)
    
    puts "\n3. reject:".colorize(:yellow)
    odds = data.reject { |n| n.even? }
    puts "  奇数: #{odds}".colorize(:green)
    
    puts "\n4. reduce/inject:".colorize(:yellow)
    sum = data.reduce(0) { |acc, n| acc + n }
    puts "  求和: #{sum}".colorize(:green)
    
    product = data.inject(1, :*)
    puts "  求积: #{product}".colorize(:green)
  end
  
  def self.demonstrate_advanced_blocks
    puts "\n=== Ruby高级块特性演示 ===\n".colorize(:blue)
    
    puts "1. 块作为对象:".colorize(:yellow)
    my_proc = proc { |x| x * 2 }
    my_lambda = lambda { |x| x + 1 }
    
    puts "  Proc调用: #{my_proc.call(5)}".colorize(:green)
    puts "  Lambda调用: #{my_lambda.call(5)}".colorize(:green)
    
    puts "\n2. 块的作用域:".colorize(:yellow)
    x = 10
    [1, 2, 3].each { |n| x += n }
    puts "  外部变量x现在是: #{x}".colorize(:green)
  end
  
  def self.run_all_demos
    demonstrate_basic_blocks
    demonstrate_iterators
    demonstrate_advanced_blocks
  end
end