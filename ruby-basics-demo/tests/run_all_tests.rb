# 运行所有测试的主脚本

require_relative 'test_helper'

# 加载所有测试文件
test_files = Dir[File.join(__dir__, '*_test.rb')]

puts "🧪 Ruby基础演示项目测试套件"
puts "=" * 50
puts "发现 #{test_files.size} 个测试文件:"

test_files.each do |file|
  test_name = File.basename(file, '.rb')
  puts "  - #{test_name}"
end

puts "\n开始运行测试..."
puts "=" * 50

# 加载并运行所有测试
test_files.each do |file|
  require file
end

# 如果直接运行此文件，打印总结
if __FILE__ == $0
  puts "\n" + "=" * 50
  puts "✅ 测试套件运行完成！"
  puts "请查看上方的测试结果。"
  
  # 提供一些有用的信息
  puts "\n📊 测试统计:"
  puts "- 测试文件数: #{test_files.size}"
  puts "- 测试类数: #{Minitest::Test.runnables.size}"
  
  total_tests = Minitest::Test.runnables.sum do |runnable|
    runnable.runnable_methods.size
  end
  puts "- 总测试方法数: #{total_tests}"
  
  puts "\n🎯 如需运行特定测试:"
  puts "ruby tests/basic_syntax_test.rb"
  puts "ruby tests/collections_test.rb"
  puts "ruby tests/exercise_system_test.rb"
  puts "ruby tests/integration_test.rb"
end