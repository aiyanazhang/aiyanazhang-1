# Ruby控制结构演示模块
# 演示Ruby中的条件语句、循环结构和流程控制

class ControlStructuresDemo
  def initialize
    @demo_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    @sample_scores = [85, 92, 78, 96, 88, 73, 91, 82]
    @weather_conditions = ['sunny', 'rainy', 'cloudy', 'snowy', 'windy']
  end
  
  # 演示if/elsif/else条件语句
  def demonstrate_if_statements
    puts "=== Ruby条件语句演示 ===\n".colorize(:blue)
    
    # 基本if语句
    puts "1. 基本if语句:".colorize(:yellow)
    age = 25
    if age >= 18
      puts "   年龄 #{age}: 已成年".colorize(:green)
    end
    
    # if/else语句
    puts "\n2. if/else语句:".colorize(:yellow)
    temperature = 15
    if temperature > 20
      puts "   温度 #{temperature}°C: 天气温暖".colorize(:green)
    else
      puts "   温度 #{temperature}°C: 天气寒冷".colorize(:green)
    end
    
    # if/elsif/else语句
    puts "\n3. if/elsif/else语句:".colorize(:yellow)
    score = 87
    if score >= 90
      puts "   分数 #{score}: 优秀".colorize(:green)
    elsif score >= 80
      puts "   分数 #{score}: 良好".colorize(:green)
    elsif score >= 70
      puts "   分数 #{score}: 中等".colorize(:green)
    else
      puts "   分数 #{score}: 需要努力".colorize(:green)
    end
    
    # 后置if语句
    puts "\n4. 后置if语句(修饰符形式):".colorize(:yellow)
    name = "Ruby"
    puts "   欢迎使用 #{name}!" if name == "Ruby"
    puts "   这是条件成立时才执行的语句".colorize(:green)
    
    # 三元运算符
    puts "\n5. 三元运算符 (condition ? true_value : false_value):".colorize(:yellow)
    number = 42
    result = number.even? ? "偶数" : "奇数"
    puts "   #{number} 是 #{result}".colorize(:green)
    
    # unless语句（if的反义）
    puts "\n6. unless语句 (if的反义):".colorize(:yellow)
    logged_in = false
    unless logged_in
      puts "   请先登录".colorize(:green)
    end
    
    # 后置unless
    puts "   访问被拒绝" unless logged_in
  end
  
  # 演示case/when语句
  def demonstrate_case_statements
    puts "\n=== Ruby case/when语句演示 ===\n".colorize(:blue)
    
    # 基本case语句
    puts "1. 基本case语句:".colorize(:yellow)
    day = 'Monday'
    case day
    when 'Monday'
      puts "   #{day}: 新的一周开始!".colorize(:green)
    when 'Tuesday', 'Wednesday', 'Thursday'
      puts "   #{day}: 工作日".colorize(:green)
    when 'Friday'
      puts "   #{day}: 感谢上帝，终于到周五了!".colorize(:green)
    when 'Saturday', 'Sunday'
      puts "   #{day}: 周末时光".colorize(:green)
    else
      puts "   #{day}: 未知的日期".colorize(:green)
    end
    
    # case语句与范围
    puts "\n2. case语句与范围:".colorize(:yellow)
    student_age = 20
    case student_age
    when 0..12
      puts "   年龄 #{student_age}: 小学生".colorize(:green)
    when 13..15
      puts "   年龄 #{student_age}: 初中生".colorize(:green)
    when 16..18
      puts "   年龄 #{student_age}: 高中生".colorize(:green)
    when 19..22
      puts "   年龄 #{student_age}: 大学生".colorize(:green)
    else
      puts "   年龄 #{student_age}: 其他".colorize(:green)
    end
    
    # case语句与正则表达式
    puts "\n3. case语句与正则表达式:".colorize(:yellow)
    email = "user@example.com"
    case email
    when /\A[\w+\-.]+@[a-z\d\-.]+\.[a-z]+\z/i
      puts "   #{email}: 有效的邮箱地址".colorize(:green)
    else
      puts "   #{email}: 无效的邮箱地址".colorize(:green)
    end
    
    # case语句与类型检查
    puts "\n4. case语句与类型检查:".colorize(:yellow)
    [42, "hello", [1, 2, 3], { name: "Ruby" }].each do |item|
      description = case item
                   when Integer
                     "整数: #{item}"
                   when String
                     "字符串: '#{item}'"
                   when Array
                     "数组，长度: #{item.length}"
                   when Hash
                     "哈希，键: #{item.keys.join(', ')}"
                   else
                     "未知类型: #{item.class}"
                   end
      puts "   #{description}".colorize(:green)
    end
    
    # case语句与lambda
    puts "\n5. case语句与lambda表达式:".colorize(:yellow)
    positive = ->(x) { x > 0 }
    negative = ->(x) { x < 0 }
    zero = ->(x) { x == 0 }
    
    [-5, 0, 3].each do |num|
      result = case num
               when positive
                 "正数"
               when negative
                 "负数"
               when zero
                 "零"
               end
      puts "   #{num} 是 #{result}".colorize(:green)
    end
  end
  
  # 演示while和until循环
  def demonstrate_while_until_loops
    puts "\n=== Ruby while和until循环演示 ===\n".colorize(:blue)
    
    # while循环
    puts "1. while循环:".colorize(:yellow)
    count = 1
    puts "   倒计时:"
    while count <= 5
      puts "     #{count}"
      count += 1
    end
    puts "   发射!".colorize(:green)
    
    # 后置while
    puts "\n2. 后置while循环:".colorize(:yellow)
    number = 1
    begin
      puts "   数字: #{number}"
      number += 1
    end while number <= 3
    
    # until循环（while的反义）
    puts "\n3. until循环 (while的反义):".colorize(:yellow)
    countdown = 5
    puts "   until循环倒计时:"
    until countdown == 0
      puts "     #{countdown}"
      countdown -= 1
    end
    puts "   完成!".colorize(:green)
    
    # 后置until
    puts "\n4. 后置until循环:".colorize(:yellow)
    tries = 0
    begin
      tries += 1
      puts "   尝试次数: #{tries}"
    end until tries >= 3
    
    # 无限循环与break
    puts "\n5. 无限循环与break:".colorize(:yellow)
    puts "   使用break跳出无限循环:"
    counter = 0
    loop do
      counter += 1
      puts "     循环 #{counter}"
      break if counter >= 3
    end
    puts "   循环结束".colorize(:green)
  end
  
  # 演示for循环和范围
  def demonstrate_for_loops_ranges
    puts "\n=== Ruby for循环和范围演示 ===\n".colorize(:blue)
    
    # 基本for循环
    puts "1. 基本for循环:".colorize(:yellow)
    puts "   遍历范围 1..5:"
    for i in 1..5
      puts "     #{i}"
    end
    
    # for循环遍历数组
    puts "\n2. for循环遍历数组:".colorize(:yellow)
    fruits = ['苹果', '香蕉', '橙子']
    puts "   遍历水果数组:"
    for fruit in fruits
      puts "     我喜欢#{fruit}"
    end
    
    # 范围演示
    puts "\n3. Ruby范围(Range)演示:".colorize(:yellow)
    puts "   包含范围 (1..5): #{(1..5).to_a}"
    puts "   排除范围 (1...5): #{(1...5).to_a}"
    puts "   字符范围 ('a'..'e'): #{('a'..'e').to_a}"
    puts "   反向范围: #{5.downto(1).to_a}"
    puts "   步进范围: #{(1..10).step(2).to_a}"
    
    # 范围方法
    puts "\n4. 范围方法:".colorize(:yellow)
    range = 1..10
    puts "   范围 #{range}:"
    puts "     包含5? #{range.include?(5)}"
    puts "     覆盖1-20? #{range.cover?(1..20)}"
    puts "     最小值: #{range.min}"
    puts "     最大值: #{range.max}"
    puts "     大小: #{range.size}"
    
    # 范围在条件中的使用
    puts "\n5. 范围在条件中的使用:".colorize(:yellow)
    @sample_scores.each do |score|
      grade = case score
              when 90..100
                'A'
              when 80..89
                'B'
              when 70..79
                'C'
              when 60..69
                'D'
              else
                'F'
              end
      puts "   分数 #{score}: 等级 #{grade}".colorize(:green)
    end
  end
  
  # 演示break和next
  def demonstrate_break_next
    puts "\n=== Ruby break和next演示 ===\n".colorize(:blue)
    
    # break语句
    puts "1. break语句 - 跳出循环:".colorize(:yellow)
    puts "   查找第一个偶数:"
    @demo_data.each do |num|
      if num.even?
        puts "     找到偶数: #{num}".colorize(:green)
        break
      else
        puts "     #{num} 是奇数，继续查找"
      end
    end
    
    # next语句（跳过当前迭代）
    puts "\n2. next语句 - 跳过当前迭代:".colorize(:yellow)
    puts "   只处理偶数:"
    @demo_data.each do |num|
      next if num.odd?  # 跳过奇数
      puts "     处理偶数: #{num}".colorize(:green)
    end
    
    # break在嵌套循环中
    puts "\n3. break在嵌套循环中:".colorize(:yellow)
    puts "   查找乘积大于20的数字对:"
    (1..5).each do |i|
      (1..5).each do |j|
        product = i * j
        if product > 20
          puts "     找到: #{i} × #{j} = #{product}".colorize(:green)
          break
        end
      end
    end
    
    # 带标签的break（使用catch/throw）
    puts "\n4. 带标签的break (catch/throw):".colorize(:yellow)
    puts "   在嵌套循环中使用catch/throw:"
    result = catch(:found) do
      (1..5).each do |i|
        (1..5).each do |j|
          product = i * j
          if product > 15
            puts "     找到目标: #{i} × #{j} = #{product}".colorize(:green)
            throw(:found, "#{i},#{j}")
          end
        end
      end
      "未找到"
    end
    puts "   结果: #{result}".colorize(:green)
    
    # redo语句（重新执行当前迭代）
    puts "\n5. redo语句 - 重新执行当前迭代:".colorize(:yellow)
    puts "   随机数游戏（获得6才继续）:"
    attempts = 0
    (1..3).each do |round|
      attempts += 1
      random_num = rand(1..6)
      puts "     第#{round}轮，尝试#{attempts}: 掷出 #{random_num}"
      
      if random_num != 6 && attempts < 3
        redo  # 重新执行当前轮次
      end
      attempts = 0  # 重置计数器
    end
  end
  
  # 演示条件赋值
  def demonstrate_conditional_assignment
    puts "\n=== Ruby条件赋值演示 ===\n".colorize(:blue)
    
    # ||= 操作符（或等于）
    puts "1. ||= 操作符（只在变量为假值时赋值）:".colorize(:yellow)
    name = nil
    name ||= "默认名称"
    puts "   name ||= '默认名称' => #{name}".colorize(:green)
    
    name ||= "新名称"  # 不会改变，因为name已经有值了
    puts "   name ||= '新名称' => #{name}".colorize(:green)
    
    # &&= 操作符（与等于）
    puts "\n2. &&= 操作符（只在变量为真值时赋值）:".colorize(:yellow)
    value = "存在的值"
    value &&= "修改后的值"
    puts "   value &&= '修改后的值' => #{value}".colorize(:green)
    
    nil_value = nil
    nil_value &&= "不会赋值"
    puts "   nil_value &&= '不会赋值' => #{nil_value.inspect}".colorize(:green)
    
    # 多重赋值与条件
    puts "\n3. 多重赋值与条件:".colorize(:yellow)
    x, y, z = [1, 2]  # z 将是 nil
    puts "   x, y, z = [1, 2] => x=#{x}, y=#{y}, z=#{z.inspect}".colorize(:green)
    
    # 使用条件赋值提供默认值
    z ||= 3
    puts "   z ||= 3 => z=#{z}".colorize(:green)
    
    # 安全导航操作符(&.)
    puts "\n4. 安全导航操作符 (&.) - Ruby 2.3+:".colorize(:yellow)
    user = { name: "Alice", profile: { age: 25 } }
    empty_user = nil
    
    puts "   user&.dig(:profile, :age) => #{user&.dig(:profile, :age)}".colorize(:green)
    puts "   empty_user&.dig(:profile, :age) => #{empty_user&.dig(:profile, :age)}".colorize(:green)
    
    # 条件赋值在哈希中的应用
    puts "\n5. 条件赋值在哈希中的应用:".colorize(:yellow)
    config = {}
    config[:host] ||= 'localhost'
    config[:port] ||= 3000
    config[:ssl] ||= false
    
    puts "   配置默认值: #{config}".colorize(:green)
  end
  
  # 运行所有演示
  def run_all_demos
    demonstrate_if_statements
    demonstrate_case_statements
    demonstrate_while_until_loops
    demonstrate_for_loops_ranges
    demonstrate_break_next
    demonstrate_conditional_assignment
  end
  
  # 交互式演示
  def interactive_demo
    puts "\n=== 交互式控制结构演示 ===\n".colorize(:blue)
    
    puts "请输入一个数字来测试各种控制结构:"
    print "数字: "
    
    # 在实际使用中，这里应该使用gets.chomp.to_i
    # 为了演示目的，我们使用预设值
    number = rand(1..100)
    puts number.to_s.colorize(:cyan)
    
    # 演示各种判断
    puts "\n对数字 #{number} 的分析:".colorize(:yellow)
    
    # 奇偶性
    puts "奇偶性: #{number.even? ? '偶数' : '奇数'}"
    
    # 大小判断
    size_desc = case number
                when 1..10
                  "很小的数"
                when 11..50
                  "中等的数"
                when 51..90
                  "较大的数"
                else
                  "很大的数"
                end
    puts "大小: #{size_desc}"
    
    # 质数判断（简单实现）
    is_prime = number > 1 && (2...number).none? { |i| number % i == 0 }
    puts "质数: #{is_prime ? '是' : '否'}"
    
    # 数字分解
    puts "数字分解:"
    temp = number
    factors = []
    (2..temp).each do |i|
      while temp % i == 0
        factors << i
        temp /= i
        break if temp == 1
      end
      break if temp == 1
    end
    puts "  质因数: #{factors.empty? ? '无（质数）' : factors.join(' × ')}"
  end
end