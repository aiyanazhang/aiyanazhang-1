# 练习系统测试

require_relative 'test_helper'
require 'exercises/exercise_system'
require 'exercises/answer_validator'

class ExerciseSystemTest < RubyBasicsTest
  def setup
    super
    @exercise_bank = ExerciseBank.new
    @exercise_runner = ExerciseRunner.new
  end
  
  def test_exercise_creation
    exercise = Exercise.new(
      id: 'test_001',
      title: '测试练习',
      question: '这是测试题目',
      type: :code_completion,
      correct_answer: 'test = "answer"'
    )
    
    assert_instance_of Exercise, exercise
    assert_equal 'test_001', exercise.id
    assert_equal '测试练习', exercise.title
    assert_equal :code_completion, exercise.type
  end
  
  def test_exercise_answer_attempt
    exercise = Exercise.new(
      id: 'test_002',
      title: '变量赋值',
      question: '定义变量name',
      type: :code_completion,
      correct_answer: 'name = "Ruby"'
    )
    
    # 正确答案
    result = exercise.attempt_answer('name = "Ruby"')
    assert result
    assert exercise.completed?
    assert_equal 1, exercise.attempts
    
    # 重新创建练习测试错误答案
    exercise2 = Exercise.new(
      id: 'test_003',
      title: '变量赋值',
      question: '定义变量name',
      type: :code_completion,
      correct_answer: 'name = "Ruby"'
    )
    
    result = exercise2.attempt_answer('name = Ruby')
    refute result
    refute exercise2.completed?
    assert_equal 1, exercise2.attempts
  end
  
  def test_exercise_bank_creation
    assert_instance_of ExerciseBank, @exercise_bank
    exercises = @exercise_bank.all_exercises
    refute_empty exercises
    
    # 检查是否有不同类型的练习
    types = exercises.map(&:type).uniq
    assert_includes types, :code_completion
    assert_includes types, :multiple_choice
    assert_includes types, :output_prediction
  end
  
  def test_exercise_bank_filtering
    # 按主题筛选
    variable_exercises = @exercise_bank.get_exercises_by_topic('variables')
    refute_empty variable_exercises
    
    # 按难度筛选
    beginner_exercises = @exercise_bank.exercises_by_difficulty(:beginner)
    refute_empty beginner_exercises
    
    # 按ID获取练习
    exercise = @exercise_bank.get_exercise_by_id('basic_001')
    refute_nil exercise
    assert_equal 'basic_001', exercise.id
  end
  
  def test_exercise_runner_creation
    assert_instance_of ExerciseRunner, @exercise_runner
  end
  
  def test_exercise_system_demo
    assert_output_includes "🎓 Ruby练习系统演示" do
      ExerciseSystem.run_demo
    end
  end
  
  def test_answer_validator_syntax_check
    assert AnswerValidator.validate_syntax('name = "Ruby"')
    refute AnswerValidator.validate_syntax('name = "Ruby')
  end
  
  def test_answer_validator_code_validation
    # 测试有效代码
    result = AnswerValidator.validate_ruby_code('name = "Ruby"')
    assert result[:valid]
    assert_nil result[:error]
    
    # 测试无效语法
    result = AnswerValidator.validate_ruby_code('name = "Ruby')
    refute result[:valid]
    assert_equal "语法错误", result[:error]
  end
  
  def test_answer_validator_output_validation
    code = 'puts "Hello"'
    expected_output = "Hello\n"
    
    result = AnswerValidator.validate_ruby_code(code, expected_output)
    assert result[:valid]
    assert_equal expected_output, result[:expected_output]
  end
  
  def test_answer_validator_behavior_validation
    code = 'x = 42'
    behavior = { type: :variable_assignment, variable: :x, value: 42 }
    
    result = AnswerValidator.validate_ruby_code(code, nil, behavior)
    assert result[:valid]
    assert_includes result[:message], "变量x正确赋值"
  end
  
  def test_answer_validator_code_quality
    code = <<~CODE
      def calculate_area(length,width)
      area=length*width
      puts area
      end
    CODE
    
    analysis = AnswerValidator.analyze_code_quality(code)
    assert_instance_of Integer, analysis[:score]
    assert analysis[:score] >= 0
    assert analysis[:score] <= 100
    assert_instance_of Array, analysis[:issues]
    assert_instance_of Array, analysis[:suggestions]
    
    # 应该发现一些代码质量问题
    refute_empty analysis[:issues]
  end
  
  def test_validator_demo
    assert_output_includes "🔍 Ruby答案验证器演示" do
      ValidatorDemo.run_demo
    end
  end
  
  # 集成测试
  def test_complete_exercise_workflow
    # 获取一个练习
    exercise = @exercise_bank.get_exercise_by_id('basic_001')
    refute_nil exercise
    
    # 模拟答题过程
    wrong_answer = 'name = Ruby'  # 缺少引号
    correct_answer = 'name = "Ruby"'
    
    # 第一次答错
    result1 = exercise.attempt_answer(wrong_answer)
    refute result1
    refute exercise.completed?
    assert_equal 1, exercise.attempts
    
    # 第二次答对
    result2 = exercise.attempt_answer(correct_answer)
    assert result2
    assert exercise.completed?
    assert_equal 2, exercise.attempts
  end
end