# Ruby模块与混入系统演示
# 展示Ruby模块的定义、使用和混入机制

# 基础模块演示
module Greeting
  WELCOME_MESSAGE = "欢迎使用Ruby模块系统!"
  
  def say_hello
    puts "Hello from Greeting module!"
  end
  
  def say_goodbye
    puts "Goodbye from Greeting module!"
  end
  
  module_function :say_hello, :say_goodbye
end

# 命名空间模块
module Math
  PI = 3.14159
  
  module Geometry
    def self.circle_area(radius)
      Math::PI * radius ** 2
    end
    
    def self.rectangle_area(width, height)
      width * height
    end
  end
  
  module Statistics
    def self.average(numbers)
      numbers.sum.to_f / numbers.size
    end
    
    def self.median(numbers)
      sorted = numbers.sort
      mid = sorted.size / 2
      sorted.size.odd? ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2.0
    end
  end
end

# 可混入的功能模块
module Comparable
  def ==(other)
    compare_to(other) == 0
  end
  
  def <(other)
    compare_to(other) < 0
  end
  
  def >(other)
    compare_to(other) > 0
  end
  
  def <=(other)
    self < other || self == other
  end
  
  def >=(other)
    self > other || self == other
  end
end

# 使用模块的类
class Version
  include Comparable
  
  attr_reader :major, :minor, :patch
  
  def initialize(version_string)
    @major, @minor, @patch = version_string.split('.').map(&:to_i)
  end
  
  def to_s
    "#{@major}.#{@minor}.#{@patch}"
  end
  
  private
  
  def compare_to(other)
    [major, minor, patch] <=> [other.major, other.minor, other.patch]
  end
end

# 模块演示主类
class ModulesDemo
  def self.run_basic_module_demo
    puts "=== Ruby基础模块演示 ===\n".colorize(:blue)
    
    puts "1. 模块常量:".colorize(:yellow)
    puts "   Greeting::WELCOME_MESSAGE: #{Greeting::WELCOME_MESSAGE}".colorize(:green)
    puts "   Math::PI: #{Math::PI}".colorize(:green)
    
    puts "\n2. 模块方法调用:".colorize(:yellow)
    Greeting.say_hello
    Greeting.say_goodbye
    
    puts "\n3. 命名空间使用:".colorize(:yellow)
    puts "   圆形面积(半径5): #{Math::Geometry.circle_area(5)}".colorize(:green)
    puts "   矩形面积(3x4): #{Math::Geometry.rectangle_area(3, 4)}".colorize(:green)
    
    numbers = [1, 2, 3, 4, 5]
    puts "   数组#{numbers}的平均值: #{Math::Statistics.average(numbers)}".colorize(:green)
    puts "   数组#{numbers}的中位数: #{Math::Statistics.median(numbers)}".colorize(:green)
  end
  
  def self.run_mixin_demo
    puts "\n=== Ruby模块混入演示 ===\n".colorize(:blue)
    
    puts "1. 创建Version对象:".colorize(:yellow)
    v1 = Version.new("2.0.1")
    v2 = Version.new("2.1.0")
    v3 = Version.new("1.9.3")
    
    puts "   v1: #{v1}".colorize(:green)
    puts "   v2: #{v2}".colorize(:green)
    puts "   v3: #{v3}".colorize(:green)
    
    puts "\n2. 使用混入的比较方法:".colorize(:yellow)
    puts "   v1 < v2: #{v1 < v2}".colorize(:green)
    puts "   v2 > v3: #{v2 > v3}".colorize(:green)
    puts "   v1 == v2: #{v1 == v2}".colorize(:green)
    
    puts "\n3. 排序:".colorize(:yellow)
    versions = [v1, v2, v3]
    sorted_versions = versions.sort
    puts "   排序前: #{versions.map(&:to_s)}".colorize(:green)
    puts "   排序后: #{sorted_versions.map(&:to_s)}".colorize(:green)
  end
  
  def self.run_all_demos
    run_basic_module_demo
    run_mixin_demo
  end
end