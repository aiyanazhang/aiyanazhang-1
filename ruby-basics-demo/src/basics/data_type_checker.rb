# Ruby数据类型检查和验证工具
# 提供各种数据类型的检查方法和实用工具

class DataTypeChecker
  # 检查变量的详细信息
  def self.inspect_variable(var, var_name = 'variable')
    puts "=== #{var_name} 详细信息 ===".colorize(:blue)
    puts "值: #{var.inspect}".colorize(:green)
    puts "类型: #{var.class}".colorize(:green)
    puts "对象ID: #{var.object_id}".colorize(:green)
    puts "祖先链: #{var.class.ancestors.first(5).join(' < ')}".colorize(:yellow)
    
    # 检查响应的方法
    interesting_methods = %w[to_s to_i to_f to_a to_h length size empty? nil?]
    available_methods = interesting_methods.select { |method| var.respond_to?(method) }
    puts "可用方法: #{available_methods.join(', ')}".colorize(:cyan) unless available_methods.empty?
    
    puts
  end
  
  # 比较不同类型的变量
  def self.compare_types(*variables)
    puts "=== 类型比较 ===".colorize(:blue)
    
    variables.each_with_index do |var, index|
      puts "变量#{index + 1}: #{var.inspect} (#{var.class})".colorize(:green)
    end
    
    puts "\n相等性比较:".colorize(:yellow)
    variables.combination(2).with_index do |(var1, var2), index|
      puts "变量#{variables.index(var1) + 1} == 变量#{variables.index(var2) + 1}: #{var1 == var2}"
      puts "变量#{variables.index(var1) + 1}.eql?(变量#{variables.index(var2) + 1}): #{var1.eql?(var2)}"
      puts "变量#{variables.index(var1) + 1}.equal?(变量#{variables.index(var2) + 1}): #{var1.equal?(var2)}"
      puts "---"
    end
  end
  
  # 演示类型检查方法
  def self.demonstrate_type_checking
    puts "=== Ruby类型检查方法演示 ===\n".colorize(:blue)
    
    # 准备不同类型的变量
    string_var = "Hello"
    integer_var = 42
    float_var = 3.14
    array_var = [1, 2, 3]
    hash_var = { name: "Ruby" }
    symbol_var = :test
    nil_var = nil
    
    variables = [string_var, integer_var, float_var, array_var, hash_var, symbol_var, nil_var]
    var_names = %w[字符串 整数 浮点数 数组 哈希 符号 nil]
    
    # 使用is_a?检查
    puts "1. 使用 is_a? 检查类型:".colorize(:yellow)
    variables.zip(var_names).each do |var, name|
      puts "#{name} is_a?(String): #{var.is_a?(String)}"
    end
    
    puts "\n2. 使用 kind_of? 检查类型 (与is_a?相同):".colorize(:yellow)
    puts "整数 kind_of?(Numeric): #{integer_var.kind_of?(Numeric)}"
    puts "浮点数 kind_of?(Numeric): #{float_var.kind_of?(Numeric)}"
    
    puts "\n3. 使用 instance_of? 检查精确类型:".colorize(:yellow)
    puts "整数 instance_of?(Integer): #{integer_var.instance_of?(Integer)}"
    puts "整数 instance_of?(Numeric): #{integer_var.instance_of?(Numeric)}"
    
    puts "\n4. 使用 respond_to? 检查方法:".colorize(:yellow)
    variables.zip(var_names).each do |var, name|
      puts "#{name} respond_to?(:length): #{var.respond_to?(:length)}"
    end
    
    puts "\n5. 使用 class 获取精确类型:".colorize(:yellow)
    variables.zip(var_names).each do |var, name|
      puts "#{name}.class: #{var.class}"
    end
  end
  
  # 演示类型转换的安全性
  def self.demonstrate_safe_conversion
    puts "\n=== 安全类型转换演示 ===\n".colorize(:blue)
    
    test_values = ['42', '3.14', 'hello', '', nil, '0', 'true', 'false']
    
    puts "测试值: #{test_values.inspect}\n".colorize(:yellow)
    
    test_values.each do |value|
      puts "值: #{value.inspect}".colorize(:green)
      
      # 使用to_方法（总是返回值）
      puts "  to_i: #{value.to_i}"
      puts "  to_f: #{value.to_f}"
      puts "  to_s: #{value.to_s}"
      
      # 使用类型构造器（可能抛出异常）
      begin
        puts "  Integer(): #{Integer(value)}"
      rescue ArgumentError, TypeError => e
        puts "  Integer(): 错误 - #{e.message}".colorize(:red)
      end
      
      begin
        puts "  Float(): #{Float(value)}"
      rescue ArgumentError, TypeError => e
        puts "  Float(): 错误 - #{e.message}".colorize(:red)
      end
      
      puts
    end
  end
  
  # 演示Ruby的动态类型特性
  def self.demonstrate_dynamic_typing
    puts "=== Ruby动态类型特性演示 ===\n".colorize(:blue)
    
    # 变量可以改变类型
    dynamic_var = "开始是字符串"
    puts "1. 动态变量初始值: #{dynamic_var.inspect} (#{dynamic_var.class})".colorize(:green)
    
    dynamic_var = 42
    puts "2. 改为整数: #{dynamic_var.inspect} (#{dynamic_var.class})".colorize(:green)
    
    dynamic_var = [1, 2, 3]
    puts "3. 改为数组: #{dynamic_var.inspect} (#{dynamic_var.class})".colorize(:green)
    
    dynamic_var = { name: "Ruby" }
    puts "4. 改为哈希: #{dynamic_var.inspect} (#{dynamic_var.class})".colorize(:green)
    
    # 鸭子类型演示
    puts "\n鸭子类型演示 ('如果它像鸭子一样走路，像鸭子一样叫，那它就是鸭子'):".colorize(:yellow)
    
    def self.quack_like_duck(obj)
      if obj.respond_to?(:quack)
        obj.quack
      else
        "#{obj.class} 不会嘎嘎叫"
      end
    end
    
    # 创建两个不同的类，但都有quack方法
    duck = Struct.new(:name) do
      def quack
        "#{name} 说: 嘎嘎!"
      end
    end
    
    robot = Struct.new(:model) do
      def quack
        "机器人 #{model} 模拟: 嘎嘎!"
      end
    end
    
    duck_instance = duck.new("小黄鸭")
    robot_instance = robot.new("RX-78")
    car = "汽车"
    
    puts quack_like_duck(duck_instance)
    puts quack_like_duck(robot_instance)
    puts quack_like_duck(car)
  end
  
  # 运行所有演示
  def self.run_all_demos
    demonstrate_type_checking
    demonstrate_safe_conversion
    demonstrate_dynamic_typing
    
    puts "\n=== 变量检查示例 ===".colorize(:blue)
    inspect_variable("Hello Ruby", "示例字符串")
    inspect_variable([1, 2, 3, 4, 5], "示例数组")
    
    puts "=== 类型比较示例 ===".colorize(:blue)
    compare_types("42", 42, 42.0, :forty_two)
  end
end