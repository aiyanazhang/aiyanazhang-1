# 集成测试 - 测试整个系统的集成和交互

require_relative 'test_helper'
require 'config_manager'

class IntegrationTest < RubyBasicsTest
  def setup
    super
    @config = ConfigManager.new('config/test_settings.yml')
  end
  
  def test_config_manager
    # 测试配置管理器基本功能
    assert_instance_of ConfigManager, @config
    
    # 测试获取配置
    assert_equal true, @config.get('display.colors')
    assert_equal 'info', @config.get('system.log_level')
    
    # 测试设置配置
    @config.set('display.colors', false)
    assert_equal false, @config.get('display.colors')
    
    # 测试便捷方法
    refute @config.colors_enabled?
    assert @config.should_clear_screen?
  end
  
  def test_main_program_structure
    # 测试主程序文件存在
    main_file = File.join(File.dirname(__dir__), 'main.rb')
    assert File.exist?(main_file), "主程序文件应该存在"
    
    # 测试主程序语法正确
    assert AnswerValidator.validate_syntax(File.read(main_file))
  end
  
  def test_all_modules_loadable
    # 测试所有模块都可以正确加载
    modules_to_test = [
      'basics/variables_demo',
      'basics/data_type_checker', 
      'basics/control_structures_demo',
      'collections/array_demo',
      'collections/hash_demo',
      'collections/collections_utils',
      'oop/oop_demo',
      'modules/modules_demo',
      'blocks/blocks_demo',
      'files/files_demo',
      'exercises/exercise_system',
      'exercises/answer_validator'
    ]
    
    modules_to_test.each do |module_path|
      assert_nothing_raised("模块 #{module_path} 应该可以正确加载") do
        require module_path
      end
    end
  end
  
  def test_system_classes_exist
    # 测试主要类是否都存在
    expected_classes = [
      'VariablesDemo',
      'DataTypeChecker', 
      'ControlStructuresDemo',
      'ArrayDemo',
      'HashDemo',
      'CollectionsUtils',
      'OOPDemo',
      'ModulesDemo',
      'BlocksDemo',
      'FilesDemo',
      'ExerciseSystem',
      'AnswerValidator',
      'ConfigManager'
    ]
    
    expected_classes.each do |class_name|
      assert Object.const_defined?(class_name), "类 #{class_name} 应该存在"
    end
  end
  
  def test_demo_classes_have_run_methods
    # 测试演示类都有运行方法
    demo_classes = [VariablesDemo, ArrayDemo, HashDemo, OOPDemo, ModulesDemo, BlocksDemo, FilesDemo]
    
    demo_classes.each do |demo_class|
      if demo_class.instance_methods.include?(:run_all_demos)
        assert_respond_to demo_class.new, :run_all_demos
      elsif demo_class.methods.include?(:run_all_demos)
        assert_respond_to demo_class, :run_all_demos
      else
        flunk "#{demo_class} 应该有 run_all_demos 方法"
      end
    end
  end
  
  def test_system_utilities_have_demo_methods
    # 测试工具类都有演示方法
    utility_classes = [DataTypeChecker, CollectionsUtils, ExerciseSystem, ValidatorDemo]
    
    utility_classes.each do |utility_class|
      if utility_class.methods.include?(:run_all_demos)
        assert_respond_to utility_class, :run_all_demos
      elsif utility_class.methods.include?(:run_demo)
        assert_respond_to utility_class, :run_demo
      else
        # 某些工具类可能有其他的演示方法
        demo_methods = utility_class.methods.grep(/demo|run/)
        refute_empty demo_methods, "#{utility_class} 应该有演示方法"
      end
    end
  end
  
  def test_file_structure_integrity
    # 测试项目文件结构完整性
    project_root = File.dirname(__dir__)
    
    required_directories = %w[src config tests docs data examples]
    required_directories.each do |dir|
      dir_path = File.join(project_root, dir)
      assert Dir.exist?(dir_path), "目录 #{dir} 应该存在"
    end
    
    required_files = %w[main.rb Gemfile README.md LICENSE]
    required_files.each do |file|
      file_path = File.join(project_root, file)
      assert File.exist?(file_path), "文件 #{file} 应该存在"
    end
  end
  
  def test_src_subdirectories_exist
    # 测试src子目录结构
    src_dir = File.join(File.dirname(__dir__), 'src')
    
    required_subdirs = %w[basics collections oop modules blocks files exercises]
    required_subdirs.each do |subdir|
      subdir_path = File.join(src_dir, subdir)
      assert Dir.exist?(subdir_path), "src/#{subdir} 目录应该存在"
    end
  end
  
  def test_ruby_files_syntax
    # 测试所有Ruby文件的语法正确性
    project_root = File.dirname(__dir__)
    ruby_files = Dir.glob(File.join(project_root, '**', '*.rb'))
    
    syntax_errors = []
    ruby_files.each do |file|
      begin
        content = File.read(file)
        unless AnswerValidator.validate_syntax(content)
          syntax_errors << file
        end
      rescue => e
        syntax_errors << "#{file}: #{e.message}"
      end
    end
    
    assert_empty syntax_errors, "以下文件有语法错误: #{syntax_errors.join(', ')}"
  end
  
  def test_demonstration_output_quality
    # 测试演示输出质量
    demo = VariablesDemo.new
    
    output, _error = capture_output do
      demo.demonstrate_variables
    end
    
    # 检查输出质量
    assert_includes output, "==="  # 应该有标题格式
    refute_empty output.strip      # 不应该是空输出
    assert output.lines.count > 5  # 应该有足够的输出内容
  end
  
  def test_error_handling
    # 测试错误处理能力
    validator = AnswerValidator
    
    # 测试无效代码不会导致系统崩溃
    result = validator.validate_ruby_code('invalid ruby code @@@@')
    refute result[:valid]
    assert_includes result[:error], "语法错误"
  end
  
  def test_system_performance
    # 基本的性能测试
    start_time = Time.now
    
    # 运行一个完整的演示
    demo = VariablesDemo.new
    capture_output { demo.run_all_demos }
    
    end_time = Time.now
    execution_time = end_time - start_time
    
    # 演示应该在合理时间内完成（比如10秒内）
    assert execution_time < 10, "演示执行时间过长: #{execution_time}秒"
  end
  
  def teardown
    super
    # 清理测试配置文件
    test_config = 'config/test_settings.yml'
    File.delete(test_config) if File.exist?(test_config)
  end
end