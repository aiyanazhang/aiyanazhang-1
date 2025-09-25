# 测试辅助工具
# 为测试提供通用的工具和配置

require 'minitest/autorun'
require 'minitest/reporters'

# 配置测试报告器
Minitest::Reporters.use! [
  Minitest::Reporters::DefaultReporter.new(color: true, slow_count: 5)
]

# 添加项目根目录到加载路径
$LOAD_PATH.unshift File.expand_path('../src', __dir__)
$LOAD_PATH.unshift File.expand_path('../config', __dir__)

# 测试基类
class RubyBasicsTest < Minitest::Test
  def setup
    # 在每个测试前执行
    @original_stdout = $stdout
    @original_stderr = $stderr
  end
  
  def teardown
    # 在每个测试后执行
    $stdout = @original_stdout
    $stderr = @original_stderr
  end
  
  # 捕获输出的辅助方法
  def capture_output
    captured_stdout = StringIO.new
    captured_stderr = StringIO.new
    
    $stdout = captured_stdout
    $stderr = captured_stderr
    
    begin
      yield
    ensure
      $stdout = @original_stdout
      $stderr = @original_stderr
    end
    
    [captured_stdout.string, captured_stderr.string]
  end
  
  # 断言输出包含特定内容
  def assert_output_includes(expected, &block)
    output, _error = capture_output(&block)
    assert_includes output, expected, "输出中应该包含: #{expected}"
  end
  
  # 断言没有错误输出
  def assert_no_errors(&block)
    _output, error = capture_output(&block)
    assert_empty error, "不应该有错误输出，但得到: #{error}"
  end
  
  # 断言代码可以正常执行
  def assert_code_runs(code)
    assert_nothing_raised("代码应该可以正常执行") do
      eval(code)
    end
  end
  
  # 断言代码会抛出特定错误
  def assert_code_raises(error_class, code)
    assert_raises(error_class, "代码应该抛出#{error_class}") do
      eval(code)
    end
  end
end

# 模拟用户输入的辅助方法
class StringIO
  def simulate_user_input(input)
    @input_buffer = input.lines
    @input_index = 0
    
    # 重写gets方法来返回模拟输入
    def gets
      return nil if @input_index >= @input_buffer.size
      line = @input_buffer[@input_index]
      @input_index += 1
      line
    end
  end
end

puts "测试环境已加载"