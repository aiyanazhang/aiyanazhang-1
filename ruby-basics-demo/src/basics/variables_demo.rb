# Ruby基础语法演示 - 变量与数据类型
# 本模块演示Ruby中的各种变量类型和基本数据类型

class VariablesDemo
  # 类变量演示
  @@class_count = 0
  
  def initialize
    # 实例变量演示
    @instance_name = 'Ruby学习者'
    @@class_count += 1
  end
  
  # 演示所有变量类型
  def demonstrate_variables
    puts "=== Ruby变量类型演示 ===\n".colorize(:blue)
    
    # 局部变量
    local_var = '这是局部变量'
    puts "1. 局部变量: #{local_var}".colorize(:green)
    
    # 实例变量
    puts "2. 实例变量: #{@instance_name}".colorize(:green)
    
    # 类变量
    puts "3. 类变量: 已创建 #{@@class_count} 个实例".colorize(:green)
    
    # 全局变量
    $global_var = '这是全局变量'
    puts "4. 全局变量: #{$global_var}".colorize(:green)
    
    # 常量
    CONSTANT_VAR = '这是常量'
    puts "5. 常量: #{CONSTANT_VAR}".colorize(:green)
    
    puts "\n变量命名规则说明:".colorize(:yellow)
    puts "- 局部变量: 小写字母或下划线开头"
    puts "- 实例变量: @开头"
    puts "- 类变量: @@开头"
    puts "- 全局变量: $开头"
    puts "- 常量: 大写字母开头"
  end
  
  # 演示数字类型
  def demonstrate_numbers
    puts "\n=== Ruby数字类型演示 ===\n".colorize(:blue)
    
    # 整数
    integer_num = 42
    puts "1. 整数 (Integer): #{integer_num}, 类型: #{integer_num.class}".colorize(:green)
    
    # 浮点数
    float_num = 3.14159
    puts "2. 浮点数 (Float): #{float_num}, 类型: #{float_num.class}".colorize(:green)
    
    # 大整数
    big_integer = 12345678901234567890
    puts "3. 大整数: #{big_integer}, 类型: #{big_integer.class}".colorize(:green)
    
    # 有理数
    rational_num = Rational(22, 7)
    puts "4. 有理数 (Rational): #{rational_num}, 小数形式: #{rational_num.to_f}".colorize(:green)
    
    # 复数
    complex_num = Complex(3, 4)
    puts "5. 复数 (Complex): #{complex_num}".colorize(:green)
    
    # 数字运算示例
    puts "\n数字运算示例:".colorize(:yellow)
    puts "加法: #{integer_num} + #{float_num} = #{integer_num + float_num}"
    puts "乘方: #{integer_num} ** 2 = #{integer_num ** 2}"
    puts "取模: #{integer_num} % 5 = #{integer_num % 5}"
  end
  
  # 演示字符串类型
  def demonstrate_strings
    puts "\n=== Ruby字符串演示 ===\n".colorize(:blue)
    
    # 基本字符串
    single_quote_str = '单引号字符串'
    double_quote_str = "双引号字符串"
    puts "1. 单引号字符串: #{single_quote_str}".colorize(:green)
    puts "2. 双引号字符串: #{double_quote_str}".colorize(:green)
    
    # 字符串插值
    name = "Ruby"
    version = 3.0
    interpolated_str = "#{name} 版本 #{version}"
    puts "3. 字符串插值: #{interpolated_str}".colorize(:green)
    
    # 多行字符串
    multiline_str = <<~HEREDOC
      这是多行字符串
      使用heredoc语法
      可以保持格式
    HEREDOC
    puts "4. 多行字符串:\n#{multiline_str}".colorize(:green)
    
    # 字符串方法演示
    puts "\n字符串方法演示:".colorize(:yellow)
    sample_string = "Hello Ruby World"
    puts "原字符串: '#{sample_string}'"
    puts "长度: #{sample_string.length}"
    puts "大写: #{sample_string.upcase}"
    puts "小写: #{sample_string.downcase}"
    puts "反转: #{sample_string.reverse}"
    puts "包含'Ruby': #{sample_string.include?('Ruby')}"
    puts "替换'World'为'Universe': #{sample_string.gsub('World', 'Universe')}"
  end
  
  # 演示符号类型
  def demonstrate_symbols
    puts "\n=== Ruby符号(Symbol)演示 ===\n".colorize(:blue)
    
    # 基本符号
    symbol1 = :hello
    symbol2 = :world
    puts "1. 基本符号: #{symbol1}, #{symbol2}".colorize(:green)
    
    # 符号与字符串的区别
    string1 = "hello"
    string2 = "hello"
    symbol3 = :hello
    symbol4 = :hello
    
    puts "\n符号与字符串的区别:".colorize(:yellow)
    puts "字符串对象ID: #{string1.object_id} vs #{string2.object_id} (不同)"
    puts "符号对象ID: #{symbol3.object_id} vs #{symbol4.object_id} (相同)"
    puts "符号不可变且唯一，适合作为标识符或键使用"
    
    # 符号转换
    puts "\n符号转换:".colorize(:yellow)
    puts "符号转字符串: #{symbol1.to_s}"
    puts "字符串转符号: #{string1.to_sym}"
    
    # 符号在哈希中的使用
    hash_with_symbols = { name: 'Ruby', version: 3.0, active: true }
    puts "使用符号作为键的哈希: #{hash_with_symbols}"
  end
  
  # 演示布尔值和nil
  def demonstrate_boolean_and_nil
    puts "\n=== Ruby布尔值和nil演示 ===\n".colorize(:blue)
    
    # 布尔值
    true_value = true
    false_value = false
    puts "1. 真值: #{true_value}, 类型: #{true_value.class}".colorize(:green)
    puts "2. 假值: #{false_value}, 类型: #{false_value.class}".colorize(:green)
    
    # nil值
    nil_value = nil
    puts "3. nil值: #{nil_value.inspect}, 类型: #{nil_value.class}".colorize(:green)
    
    # 真假值判断
    puts "\nRuby中的真假值:".colorize(:yellow)
    puts "true 是真值: #{!!true}"
    puts "false 是假值: #{!!false}"
    puts "nil 是假值: #{!!nil}"
    puts "0 是真值: #{!!0}"
    puts "空字符串 是真值: #{!!''}"
    puts "空数组 是真值: #{!![]}"
    
    puts "\n注意: 在Ruby中，只有false和nil是假值，其他都是真值!"
  end
  
  # 演示类型转换
  def demonstrate_type_conversion
    puts "\n=== Ruby类型转换演示 ===\n".colorize(:blue)
    
    # 转换为字符串
    puts "1. 转换为字符串:".colorize(:yellow)
    puts "   42.to_s => '#{42.to_s}'"
    puts "   3.14.to_s => '#{3.14.to_s}'"
    puts "   true.to_s => '#{true.to_s}'"
    puts "   nil.to_s => '#{nil.to_s}'"
    
    # 转换为整数
    puts "\n2. 转换为整数:".colorize(:yellow)
    puts "   '42'.to_i => #{42}"
    puts "   '3.14'.to_i => #{'3.14'.to_i}"
    puts "   'hello'.to_i => #{'hello'.to_i}"
    
    # 转换为浮点数
    puts "\n3. 转换为浮点数:".colorize(:yellow)
    puts "   '3.14'.to_f => #{'3.14'.to_f}"
    puts "   '42'.to_f => #{'42'.to_f}"
    
    # 转换为符号
    puts "\n4. 转换为符号:".colorize(:yellow)
    puts "   'hello'.to_sym => #{:hello}"
    puts "   :hello.to_s => #{:hello.to_s}"
    
    # 安全转换
    puts "\n5. 安全转换方法:".colorize(:yellow)
    puts "   Integer('42') => #{Integer('42')}"
    puts "   Float('3.14') => #{Float('3.14')}"
    
    begin
      Integer('hello')
    rescue ArgumentError => e
      puts "   Integer('hello') => 错误: #{e.message}"
    end
  end
  
  # 运行所有演示
  def run_all_demos
    demonstrate_variables
    demonstrate_numbers
    demonstrate_strings
    demonstrate_symbols
    demonstrate_boolean_and_nil
    demonstrate_type_conversion
  end
end