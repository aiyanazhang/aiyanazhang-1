# 基础语法模块测试

require_relative 'test_helper'
require 'basics/variables_demo'
require 'basics/data_type_checker'

class BasicSyntaxTest < RubyBasicsTest
  def setup
    super
    @variables_demo = VariablesDemo.new
    @data_checker = DataTypeChecker
  end
  
  def test_variables_demo_creation
    assert_instance_of VariablesDemo, @variables_demo
    refute_nil @variables_demo
  end
  
  def test_variables_demo_methods_exist
    assert_respond_to @variables_demo, :demonstrate_variables
    assert_respond_to @variables_demo, :demonstrate_numbers
    assert_respond_to @variables_demo, :demonstrate_strings
    assert_respond_to @variables_demo, :demonstrate_symbols
    assert_respond_to @variables_demo, :demonstrate_boolean_and_nil
    assert_respond_to @variables_demo, :demonstrate_type_conversion
  end
  
  def test_variables_demonstration_runs_without_errors
    assert_no_errors do
      @variables_demo.demonstrate_variables
    end
  end
  
  def test_variables_demonstration_output
    assert_output_includes "=== Ruby变量类型演示 ===" do
      @variables_demo.demonstrate_variables
    end
  end
  
  def test_numbers_demonstration
    assert_output_includes "=== Ruby数字类型演示 ===" do
      @variables_demo.demonstrate_numbers
    end
  end
  
  def test_strings_demonstration
    assert_output_includes "=== Ruby字符串演示 ===" do
      @variables_demo.demonstrate_strings
    end
  end
  
  def test_symbols_demonstration
    assert_output_includes "=== Ruby符号(Symbol)演示 ===" do
      @variables_demo.demonstrate_symbols
    end
  end
  
  def test_boolean_and_nil_demonstration
    assert_output_includes "=== Ruby布尔值和nil演示 ===" do
      @variables_demo.demonstrate_boolean_and_nil
    end
  end
  
  def test_type_conversion_demonstration
    assert_output_includes "=== Ruby类型转换演示 ===" do
      @variables_demo.demonstrate_type_conversion
    end
  end
  
  def test_data_type_checker_methods
    assert_respond_to @data_checker, :inspect_variable
    assert_respond_to @data_checker, :compare_types
    assert_respond_to @data_checker, :demonstrate_type_checking
    assert_respond_to @data_checker, :demonstrate_safe_conversion
    assert_respond_to @data_checker, :demonstrate_dynamic_typing
  end
  
  def test_inspect_variable_functionality
    assert_output_includes "=== variable 详细信息 ===" do
      @data_checker.inspect_variable("test", "variable")
    end
  end
  
  def test_type_checking_demonstration
    assert_output_includes "=== Ruby类型检查方法演示 ===" do
      @data_checker.demonstrate_type_checking
    end
  end
  
  def test_safe_conversion_demonstration
    assert_output_includes "=== 安全类型转换演示 ===" do
      @data_checker.demonstrate_safe_conversion
    end
  end
  
  def test_dynamic_typing_demonstration
    assert_output_includes "=== Ruby动态类型特性演示 ===" do
      @data_checker.demonstrate_dynamic_typing
    end
  end
  
  def test_run_all_demos
    assert_no_errors do
      @variables_demo.run_all_demos
    end
    
    assert_no_errors do
      @data_checker.run_all_demos
    end
  end
  
  # 测试实际的Ruby语法概念
  def test_variable_types
    # 局部变量
    local_var = "local"
    assert_equal "local", local_var
    
    # 常量
    assert_equal "Homo sapiens", Person::SPECIES if defined?(Person::SPECIES)
  end
  
  def test_data_types
    # 数字类型
    integer = 42
    float = 3.14
    assert_instance_of Integer, integer
    assert_instance_of Float, float
    
    # 字符串
    string = "Ruby"
    assert_instance_of String, string
    assert_equal 4, string.length
    
    # 符号
    symbol = :test
    assert_instance_of Symbol, symbol
    assert_equal symbol.object_id, :test.object_id
    
    # 布尔值和nil
    assert_equal TrueClass, true.class
    assert_equal FalseClass, false.class
    assert_equal NilClass, nil.class
  end
  
  def test_type_conversions
    # 字符串转换
    assert_equal "42", 42.to_s
    assert_equal "3.14", 3.14.to_s
    
    # 数字转换
    assert_equal 42, "42".to_i
    assert_equal 3.14, "3.14".to_f
    assert_equal 0, "hello".to_i
    
    # 符号转换
    assert_equal "test", :test.to_s
    assert_equal :test, "test".to_sym
  end
end