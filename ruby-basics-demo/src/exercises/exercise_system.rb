# Ruby练习系统 - 题目管理和验证机制
# 提供互动式练习和自动验证功能

require_relative 'answer_validator'

class Exercise
  attr_reader :id, :title, :question, :type, :hints, :related_topics
  attr_accessor :correct_answer, :user_answer
  
  def initialize(id:, title:, question:, type:, correct_answer:, hints: [], related_topics: [])
    @id = id
    @title = title
    @question = question
    @type = type
    @correct_answer = correct_answer
    @hints = hints
    @related_topics = related_topics
    @user_answer = nil
    @attempts = 0
    @completed = false
  end
  
  def attempt_answer(answer)
    @attempts += 1
    @user_answer = answer
    
    case @type
    when :code_completion
      validate_code_completion(answer)
    when :multiple_choice
      validate_multiple_choice(answer)
    when :output_prediction
      validate_output_prediction(answer)
    when :code_correction
      validate_code_correction(answer)
    else
      false
    end
  end
  
  def completed?
    @completed
  end
  
  def attempts
    @attempts
  end
  
  def get_hint(hint_index = 0)
    return "没有更多提示了" if hint_index >= @hints.size
    @hints[hint_index]
  end
  
  private
  
  def validate_code_completion(answer)
    # 简化的代码完成验证
    normalized_answer = answer.strip.gsub(/\s+/, ' ')
    normalized_correct = @correct_answer.strip.gsub(/\s+/, ' ')
    
    if normalized_answer == normalized_correct
      @completed = true
      true
    else
      false
    end
  end
  
  def validate_multiple_choice(answer)
    if answer.to_s.downcase == @correct_answer.to_s.downcase
      @completed = true
      true
    else
      false
    end
  end
  
  def validate_output_prediction(answer)
    if answer.strip == @correct_answer.strip
      @completed = true
      true
    else
      false
    end
  end
  
  def validate_code_correction(answer)
    # 简化的代码纠错验证
    if answer.include?(@correct_answer)
      @completed = true
      true
    else
      false
    end
  end
end

class ExerciseBank
  def initialize
    @exercises = create_exercise_bank
  end
  
  def get_exercises_by_topic(topic)
    @exercises.select { |ex| ex.related_topics.include?(topic) }
  end
  
  def get_exercise_by_id(id)
    @exercises.find { |ex| ex.id == id }
  end
  
  def all_exercises
    @exercises
  end
  
  def exercises_by_difficulty(difficulty)
    # 简化实现，基于ID范围判断难度
    case difficulty
    when :beginner
      @exercises.select { |ex| ex.id.start_with?('basic') }
    when :intermediate
      @exercises.select { |ex| ex.id.start_with?('inter') }
    when :advanced
      @exercises.select { |ex| ex.id.start_with?('adv') }
    else
      @exercises
    end
  end
  
  private
  
  def create_exercise_bank
    exercises = []
    
    # 基础语法练习
    exercises << Exercise.new(
      id: 'basic_001',
      title: '变量定义',
      question: '定义一个名为name的变量，值为"Ruby"',
      type: :code_completion,
      correct_answer: 'name = "Ruby"',
      hints: ['使用等号赋值', '字符串用双引号包围'],
      related_topics: ['variables', 'strings']
    )
    
    exercises << Exercise.new(
      id: 'basic_002',
      title: '数组创建',
      question: '创建一个包含数字1到5的数组',
      type: :code_completion,
      correct_answer: 'arr = [1, 2, 3, 4, 5]',
      hints: ['使用方括号', '用逗号分隔元素'],
      related_topics: ['arrays', 'literals']
    )
    
    exercises << Exercise.new(
      id: 'basic_003',
      title: '输出预测',
      question: "以下代码的输出是什么？\nputs 2 + 3 * 4",
      type: :output_prediction,
      correct_answer: '14',
      hints: ['注意运算符优先级', '乘法先于加法'],
      related_topics: ['operators', 'arithmetic']
    )
    
    exercises << Exercise.new(
      id: 'basic_004',
      title: '条件语句',
      question: 'Ruby中表示"如果x大于10"的条件语句开头是？',
      type: :multiple_choice,
      correct_answer: 'A',
      hints: ['A: if x > 10', 'B: if (x > 10)', 'C: when x > 10', 'D: case x > 10'],
      related_topics: ['conditionals', 'if_statements']
    )
    
    exercises << Exercise.new(
      id: 'basic_005',
      title: '哈希创建',
      question: '创建一个哈希，键为:name，值为"Alice"',
      type: :code_completion,
      correct_answer: 'hash = { name: "Alice" }',
      hints: ['使用花括号', '符号作为键', '用冒号简写'],
      related_topics: ['hashes', 'symbols']
    )
    
    # 中级练习
    exercises << Exercise.new(
      id: 'inter_001',
      title: '方法定义',
      question: '定义一个名为greet的方法，接受一个name参数并返回"Hello, #{name}!"',
      type: :code_completion,
      correct_answer: 'def greet(name)
  "Hello, #{name}!"
end',
      hints: ['使用def关键字', '使用字符串插值', 'Ruby方法自动返回最后一行'],
      related_topics: ['methods', 'string_interpolation']
    )
    
    exercises << Exercise.new(
      id: 'inter_002',
      title: '迭代器使用',
      question: '使用each方法遍历数组[1,2,3]并打印每个元素',
      type: :code_completion,
      correct_answer: '[1,2,3].each { |n| puts n }',
      hints: ['使用each方法', '使用块参数', '可以用{}或do...end'],
      related_topics: ['iterators', 'blocks', 'each']
    )
    
    exercises << Exercise.new(
      id: 'inter_003',
      title: '类定义',
      question: '定义一个Car类，有一个initialize方法接受brand参数',
      type: :code_completion,
      correct_answer: 'class Car
  def initialize(brand)
    @brand = brand
  end
end',
      hints: ['使用class关键字', 'initialize是构造方法', '使用@符号定义实例变量'],
      related_topics: ['classes', 'initialize', 'instance_variables']
    )
    
    # 高级练习
    exercises << Exercise.new(
      id: 'adv_001',
      title: '模块混入',
      question: '如何在类中包含一个名为Comparable的模块？',
      type: :code_completion,
      correct_answer: 'include Comparable',
      hints: ['使用include关键字', '在类定义内部使用'],
      related_topics: ['modules', 'mixins', 'include']
    )
    
    exercises << Exercise.new(
      id: 'adv_002',
      title: '错误代码纠正',
      question: '纠正以下代码中的错误：\nclass Person\n  def initialize name\n    @name = name\n  end',
      type: :code_correction,
      correct_answer: '(name)',
      hints: ['方法参数需要括号', '检查语法规范'],
      related_topics: ['syntax', 'methods', 'classes']
    )
    
    exercises
  end
end

class ExerciseRunner
  def initialize
    @exercise_bank = ExerciseBank.new
    @current_exercise = nil
    @progress = {}
  end
  
  def start_practice_session(topic = nil, difficulty = nil)
    exercises = if topic
                 @exercise_bank.get_exercises_by_topic(topic)
               elsif difficulty
                 @exercise_bank.exercises_by_difficulty(difficulty)
               else
                 @exercise_bank.all_exercises
               end
    
    if exercises.empty?
      puts "没有找到匹配的练习题".colorize(:yellow)
      return
    end
    
    puts "🎯 开始练习会话".colorize(:blue).bold
    puts "找到 #{exercises.size} 道练习题\n".colorize(:green)
    
    exercises.each_with_index do |exercise, index|
      puts "=" * 60
      puts "练习 #{index + 1}/#{exercises.size}: #{exercise.title}".colorize(:blue).bold
      puts "=" * 60
      
      run_single_exercise(exercise)
      
      puts "\n按回车键继续下一题...".colorize(:cyan)
      gets
    end
    
    show_session_summary(exercises)
  end
  
  def run_single_exercise(exercise)
    @current_exercise = exercise
    puts exercise.question.colorize(:yellow)
    
    if exercise.type == :multiple_choice && !exercise.hints.empty?
      puts "\n选项:".colorize(:cyan)
      exercise.hints.each { |hint| puts "  #{hint}" }
    end
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts && !exercise.completed?
      attempts += 1
      puts "\n尝试 #{attempts}/#{max_attempts}:".colorize(:cyan)
      print "你的答案: "
      
      # 在实际环境中这里会获取用户输入
      # answer = gets.chomp
      # 为了演示，我们模拟一些答案
      answer = simulate_user_answer(exercise, attempts)
      puts answer.colorize(:magenta)
      
      if exercise.attempt_answer(answer)
        puts "✅ 正确！".colorize(:green).bold
        record_progress(exercise, true, attempts)
        break
      else
        puts "❌ 答案不正确".colorize(:red)
        
        if attempts < max_attempts
          hint_index = attempts - 1
          if hint_index < exercise.hints.size
            puts "💡 提示: #{exercise.get_hint(hint_index)}".colorize(:yellow)
          end
        end
      end
    end
    
    unless exercise.completed?
      puts "\n正确答案是: #{exercise.correct_answer}".colorize(:blue)
      record_progress(exercise, false, attempts)
    end
    
    show_related_topics(exercise)
  end
  
  def show_practice_menu
    loop do
      puts "\n🎓 Ruby练习系统".colorize(:blue).bold
      puts "=" * 40
      puts "1. 基础语法练习"
      puts "2. 控制结构练习"
      puts "3. 集合操作练习"
      puts "4. 面向对象练习"
      puts "5. 随机练习"
      puts "6. 查看进度"
      puts "7. 返回主菜单"
      puts "=" * 40
      print "请选择 (1-7): ".colorize(:yellow)
      
      # 模拟用户选择
      choice = rand(1..7)
      puts choice.to_s.colorize(:cyan)
      
      case choice
      when 1
        start_practice_session('variables')
      when 2
        start_practice_session('conditionals')
      when 3
        start_practice_session('arrays')
      when 4
        start_practice_session('classes')
      when 5
        start_random_practice
      when 6
        show_progress_report
      when 7
        break
      end
    end
  end
  
  def start_random_practice
    exercises = @exercise_bank.all_exercises.sample(3)
    puts "🎲 随机选择了3道练习题".colorize(:blue)
    
    exercises.each_with_index do |exercise, index|
      puts "\n随机练习 #{index + 1}/3:"
      run_single_exercise(exercise)
    end
  end
  
  def show_progress_report
    puts "\n📊 学习进度报告".colorize(:blue).bold
    puts "=" * 50
    
    if @progress.empty?
      puts "还没有练习记录".colorize(:yellow)
      return
    end
    
    total_exercises = @progress.size
    completed_exercises = @progress.count { |_, data| data[:completed] }
    success_rate = (completed_exercises.to_f / total_exercises * 100).round(1)
    
    puts "总练习数: #{total_exercises}".colorize(:green)
    puts "完成数: #{completed_exercises}".colorize(:green)
    puts "成功率: #{success_rate}%".colorize(:green)
    
    puts "\n详细记录:".colorize(:yellow)
    @progress.each do |exercise_id, data|
      status = data[:completed] ? "✅" : "❌"
      puts "  #{status} #{exercise_id} - 尝试次数: #{data[:attempts]}"
    end
    
    puts "\n推荐练习主题:".colorize(:yellow)
    failed_topics = @progress.select { |_, data| !data[:completed] }
                              .map { |id, _| @exercise_bank.get_exercise_by_id(id)&.related_topics }
                              .flatten
                              .compact
                              .tally
    
    if failed_topics.any?
      failed_topics.sort_by { |_, count| -count }.first(3).each do |topic, count|
        puts "  - #{topic} (#{count}个需要加强)"
      end
    else
      puts "  所有主题掌握良好！🎉"
    end
  end
  
  private
  
  def simulate_user_answer(exercise, attempt)
    # 模拟用户答案，用于演示
    case exercise.id
    when 'basic_001'
      attempt == 1 ? 'name = Ruby' : 'name = "Ruby"'
    when 'basic_002'
      attempt == 1 ? '[1,2,3,4,5]' : 'arr = [1, 2, 3, 4, 5]'
    when 'basic_003'
      attempt == 1 ? '20' : '14'
    when 'basic_004'
      attempt == 1 ? 'B' : 'A'
    when 'basic_005'
      attempt == 1 ? '{ "name" => "Alice" }' : 'hash = { name: "Alice" }'
    else
      exercise.correct_answer
    end
  end
  
  def record_progress(exercise, completed, attempts)
    @progress[exercise.id] = {
      completed: completed,
      attempts: attempts,
      timestamp: Time.now
    }
  end
  
  def show_related_topics(exercise)
    unless exercise.related_topics.empty?
      puts "\n📚 相关主题: #{exercise.related_topics.join(', ')}".colorize(:cyan)
    end
  end
end

class ExerciseSystem
  def self.run_demo
    puts "🎓 Ruby练习系统演示".colorize(:blue).bold
    puts "=" * 50
    
    runner = ExerciseRunner.new
    
    # 演示单个练习
    puts "\n演示单个练习:".colorize(:yellow)
    exercise = runner.instance_variable_get(:@exercise_bank).get_exercise_by_id('basic_001')
    runner.run_single_exercise(exercise)
    
    # 演示进度报告
    puts "\n" + "=" * 50
    runner.show_progress_report
    
    puts "\n🎯 练习系统演示完成！".colorize(:green).bold
    puts "在实际使用中，用户可以通过菜单选择不同类型的练习。".colorize(:cyan)
  end
end