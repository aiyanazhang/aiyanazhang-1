# Ruby答案验证器 - 高级验证逻辑
# 提供更精确的答案验证和代码分析功能

class AnswerValidator
  def self.validate_ruby_code(user_code, expected_output = nil, expected_behavior = nil)
    begin
      # 基本语法检查
      syntax_valid = validate_syntax(user_code)
      return { valid: false, error: "语法错误" } unless syntax_valid
      
      # 如果有期望输出，验证输出
      if expected_output
        actual_output = capture_output(user_code)
        output_match = actual_output.strip == expected_output.strip
        return { 
          valid: output_match, 
          actual_output: actual_output,
          expected_output: expected_output,
          error: output_match ? nil : "输出不匹配"
        }
      end
      
      # 如果有期望行为，验证行为
      if expected_behavior
        behavior_result = validate_behavior(user_code, expected_behavior)
        return behavior_result
      end
      
      { valid: true, error: nil }
    rescue => e
      { valid: false, error: "执行错误: #{e.message}" }
    end
  end
  
  def self.validate_syntax(code)
    begin
      # 使用Ruby解析器检查语法
      RubyVM::InstructionSequence.compile(code)
      true
    rescue SyntaxError
      false
    end
  end
  
  def self.capture_output(code)
    # 在安全的环境中执行代码并捕获输出
    old_stdout = $stdout
    $stdout = StringIO.new
    
    begin
      eval(code)
      $stdout.string
    ensure
      $stdout = old_stdout
    end
  end
  
  def self.validate_behavior(code, expected_behavior)
    case expected_behavior[:type]
    when :variable_assignment
      validate_variable_assignment(code, expected_behavior)
    when :method_definition
      validate_method_definition(code, expected_behavior)
    when :class_definition
      validate_class_definition(code, expected_behavior)
    when :return_value
      validate_return_value(code, expected_behavior)
    else
      { valid: false, error: "未知的行为验证类型" }
    end
  end
  
  def self.validate_variable_assignment(code, expected)
    var_name = expected[:variable]
    expected_value = expected[:value]
    
    begin
      eval(code)
      actual_value = eval(var_name.to_s)
      
      if actual_value == expected_value
        { valid: true, message: "变量#{var_name}正确赋值为#{expected_value}" }
      else
        { valid: false, error: "变量#{var_name}的值是#{actual_value}，期望#{expected_value}" }
      end
    rescue NameError
      { valid: false, error: "变量#{var_name}未定义" }
    rescue => e
      { valid: false, error: "执行错误: #{e.message}" }
    end
  end
  
  def self.validate_method_definition(code, expected)
    method_name = expected[:method]
    expected_params = expected[:parameters] || []
    
    begin
      eval(code)
      
      if method(method_name.to_sym)
        method_obj = method(method_name.to_sym)
        actual_params = method_obj.parameters.map(&:last)
        
        if actual_params.size == expected_params.size
          { valid: true, message: "方法#{method_name}定义正确" }
        else
          { valid: false, error: "方法#{method_name}参数数量不匹配" }
        end
      else
        { valid: false, error: "方法#{method_name}未定义" }
      end
    rescue NameError
      { valid: false, error: "方法#{method_name}未定义" }
    rescue => e
      { valid: false, error: "执行错误: #{e.message}" }
    end
  end
  
  def self.validate_class_definition(code, expected)
    class_name = expected[:class]
    expected_methods = expected[:methods] || []
    
    begin
      eval(code)
      
      if Object.const_defined?(class_name)
        klass = Object.const_get(class_name)
        
        missing_methods = expected_methods - klass.instance_methods(false).map(&:to_s)
        
        if missing_methods.empty?
          { valid: true, message: "类#{class_name}定义正确" }
        else
          { valid: false, error: "类#{class_name}缺少方法: #{missing_methods.join(', ')}" }
        end
      else
        { valid: false, error: "类#{class_name}未定义" }
      end
    rescue => e
      { valid: false, error: "执行错误: #{e.message}" }
    end
  end
  
  def self.validate_return_value(code, expected)
    expected_value = expected[:value]
    
    begin
      actual_value = eval(code)
      
      if actual_value == expected_value
        { valid: true, message: "返回值正确: #{expected_value}" }
      else
        { valid: false, error: "返回值是#{actual_value}，期望#{expected_value}" }
      end
    rescue => e
      { valid: false, error: "执行错误: #{e.message}" }
    end
  end
  
  # 代码质量检查
  def self.analyze_code_quality(code)
    issues = []
    
    # 检查基本的代码风格
    issues << "建议使用2个空格缩进" if code.include?("\t")
    issues << "行末有多余空格" if code.lines.any? { |line| line.end_with?(" \n") }
    issues << "建议在操作符周围添加空格" if code.match?(/[a-zA-Z0-9][+\-*\/=][a-zA-Z0-9]/)
    
    # 检查命名约定
    issues << "变量名建议使用snake_case" if code.match?(/[a-z][A-Z]/)
    issues << "常量名建议使用UPPER_CASE" if code.match?(/^[A-Z][a-z]/)
    
    # 检查潜在问题
    issues << "发现全局变量使用，请谨慎" if code.include?('$')
    issues << "建议避免使用单字母变量名" if code.match?(/\b[a-z]\s*=/)
    
    {
      score: calculate_quality_score(issues),
      issues: issues,
      suggestions: generate_suggestions(code)
    }
  end
  
  def self.calculate_quality_score(issues)
    base_score = 100
    penalty_per_issue = 10
    [base_score - (issues.size * penalty_per_issue), 0].max
  end
  
  def self.generate_suggestions(code)
    suggestions = []
    
    suggestions << "添加注释来解释复杂逻辑" if code.lines.size > 5 && !code.include?('#')
    suggestions << "考虑将长方法拆分为多个小方法" if code.lines.size > 15
    suggestions << "使用更有意义的变量名" if code.match?(/\b(x|y|z|temp|tmp)\b/)
    
    suggestions
  end
end

# 验证器演示
class ValidatorDemo
  def self.run_demo
    puts "🔍 Ruby答案验证器演示".colorize(:blue).bold
    puts "=" * 50
    
    # 演示语法验证
    puts "\n1. 语法验证演示:".colorize(:yellow)
    
    valid_code = 'name = "Ruby"'
    invalid_code = 'name = "Ruby'
    
    puts "有效代码: #{valid_code}"
    puts "语法检查: #{AnswerValidator.validate_syntax(valid_code) ? '✅' : '❌'}"
    
    puts "无效代码: #{invalid_code}"
    puts "语法检查: #{AnswerValidator.validate_syntax(invalid_code) ? '✅' : '❌'}"
    
    # 演示输出验证
    puts "\n2. 输出验证演示:".colorize(:yellow)
    code_with_output = 'puts "Hello, Ruby!"'
    expected_output = "Hello, Ruby!\n"
    
    result = AnswerValidator.validate_ruby_code(code_with_output, expected_output)
    puts "代码: #{code_with_output}"
    puts "期望输出: #{expected_output.inspect}"
    puts "验证结果: #{result[:valid] ? '✅' : '❌'}"
    
    # 演示行为验证
    puts "\n3. 行为验证演示:".colorize(:yellow)
    variable_code = 'age = 25'
    behavior = { type: :variable_assignment, variable: :age, value: 25 }
    
    result = AnswerValidator.validate_ruby_code(variable_code, nil, behavior)
    puts "代码: #{variable_code}"
    puts "验证结果: #{result[:valid] ? '✅' : '❌'}"
    puts "消息: #{result[:message] || result[:error]}"
    
    # 演示代码质量分析
    puts "\n4. 代码质量分析演示:".colorize(:yellow)
    quality_code = <<~CODE
      def calculate_area(length,width)
      area=length*width
      puts area
      end
    CODE
    
    analysis = AnswerValidator.analyze_code_quality(quality_code)
    puts "分析代码:"
    puts quality_code
    puts "质量评分: #{analysis[:score]}/100"
    puts "发现的问题:"
    analysis[:issues].each { |issue| puts "  - #{issue}" }
    puts "改进建议:"
    analysis[:suggestions].each { |suggestion| puts "  - #{suggestion}" }
    
    puts "\n🔍 验证器演示完成！".colorize(:green).bold
  end
end