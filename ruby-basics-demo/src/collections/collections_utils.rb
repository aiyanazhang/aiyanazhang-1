# Ruby集合工具类 - 整合数组和哈希的实用工具
require_relative 'array_demo'
require_relative 'hash_demo'

class CollectionsUtils
  def self.run_interactive_demo
    puts "=== Ruby集合综合演示 ===".colorize(:blue)
    
    # 创建演示实例
    array_demo = ArrayDemo.new
    hash_demo = HashDemo.new
    
    puts "\n请选择要演示的集合类型:".colorize(:yellow)
    puts "1. 数组(Array)演示"
    puts "2. 哈希(Hash)演示"
    puts "3. 集合转换演示"
    puts "4. 综合应用示例"
    
    # 在实际应用中这里会获取用户输入
    choice = rand(1..4)
    puts "随机选择: #{choice}".colorize(:cyan)
    
    case choice
    when 1
      puts "\n=== 数组演示 ===".colorize(:blue)
      array_demo.demonstrate_array_creation
      array_demo.demonstrate_array_transformation
    when 2
      puts "\n=== 哈希演示 ===".colorize(:blue)
      hash_demo.demonstrate_hash_creation
      hash_demo.demonstrate_hash_iteration
    when 3
      demonstrate_conversions
    when 4
      demonstrate_practical_examples
    end
  end
  
  def self.demonstrate_conversions
    puts "\n=== 集合转换演示 ===".colorize(:blue)
    
    # 数组转哈希
    puts "1. 数组转哈希:".colorize(:yellow)
    pairs = [['name', 'Ruby'], ['version', 3.0], ['type', 'language']]
    hash_from_pairs = Hash[pairs]
    puts "   #{pairs} => #{hash_from_pairs}".colorize(:green)
    
    # 哈希转数组
    puts "\n2. 哈希转数组:".colorize(:yellow)
    sample_hash = { a: 1, b: 2, c: 3 }
    array_from_hash = sample_hash.to_a
    puts "   #{sample_hash} => #{array_from_hash}".colorize(:green)
    
    # 复杂转换
    puts "\n3. 复杂数据转换:".colorize(:yellow)
    data = [
      { name: 'Alice', score: 95 },
      { name: 'Bob', score: 87 },
      { name: 'Charlie', score: 92 }
    ]
    
    # 提取名字数组
    names = data.map { |person| person[:name] }
    puts "   提取名字: #{names}".colorize(:green)
    
    # 转换为名字-分数映射
    score_map = data.each_with_object({}) { |person, hash| hash[person[:name]] = person[:score] }
    puts "   分数映射: #{score_map}".colorize(:green)
  end
  
  def self.demonstrate_practical_examples
    puts "\n=== 实际应用示例 ===".colorize(:blue)
    
    # 学生成绩管理系统
    students = [
      { name: '张三', subjects: { math: 95, english: 87, physics: 92 } },
      { name: '李四', subjects: { math: 88, english: 94, physics: 85 } },
      { name: '王五', subjects: { math: 91, english: 89, physics: 96 } }
    ]
    
    puts "学生数据: #{students}".colorize(:cyan)
    
    # 计算总分
    puts "\n1. 计算每个学生的总分:".colorize(:yellow)
    students_with_total = students.map do |student|
      total = student[:subjects].values.sum
      student.merge(total: total)
    end
    students_with_total.each { |s| puts "   #{s[:name]}: #{s[:total]}分".colorize(:green) }
    
    # 计算平均分
    puts "\n2. 计算各科平均分:".colorize(:yellow)
    subject_totals = students.each_with_object(Hash.new(0)) do |student, totals|
      student[:subjects].each { |subject, score| totals[subject] += score }
    end
    
    subject_averages = subject_totals.transform_values { |total| total / students.size.to_f }
    subject_averages.each { |subject, avg| puts "   #{subject}: #{avg.round(1)}分".colorize(:green) }
    
    # 找出最高分学生
    puts "\n3. 找出总分最高的学生:".colorize(:yellow)
    top_student = students_with_total.max_by { |student| student[:total] }
    puts "   最高分: #{top_student[:name]} - #{top_student[:total]}分".colorize(:green)
  end
end