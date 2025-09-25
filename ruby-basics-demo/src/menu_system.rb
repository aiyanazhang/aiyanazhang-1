# Ruby交互式菜单系统
# 提供用户友好的命令行界面来选择和运行各种演示

require 'colorize'

# 加载所有演示模块
require_relative '../basics/variables_demo'
require_relative '../basics/data_type_checker'
require_relative '../basics/control_structures_demo'
require_relative '../collections/array_demo'
require_relative '../collections/hash_demo'
require_relative '../collections/collections_utils'
require_relative '../oop/oop_demo'
require_relative '../modules/modules_demo'
require_relative '../blocks/blocks_demo'
require_relative '../files/files_demo'

class MenuSystem
  def initialize
    @running = true
  end
  
  def start
    display_welcome
    
    while @running
      display_main_menu
      choice = get_user_choice(1, 10)
      process_main_choice(choice)
    end
    
    display_goodbye
  end
  
  private
  
  def display_welcome
    puts "\n#{'=' * 60}".colorize(:blue)
    puts "#{' ' * 15}🎯 Ruby基础教程演示系统 🎯".colorize(:blue)
    puts "#{'=' * 60}".colorize(:blue)
    puts "欢迎来到Ruby编程语言基础教程演示系统！".colorize(:green)
    puts "本系统将通过实际可运行的代码示例帮助您掌握Ruby的核心概念。".colorize(:green)
    puts "\n按回车键继续...".colorize(:yellow)
    gets
  end
  
  def display_main_menu
    clear_screen
    puts "\n🏠 主菜单".colorize(:blue).bold
    puts "#{'─' * 40}".colorize(:blue)
    puts "1. 📝 基础语法演示"
    puts "2. 🔄 控制结构演示"
    puts "3. 📊 集合操作演示"
    puts "4. 🏗️  面向对象编程演示"
    puts "5. 📦 模块与混入演示"
    puts "6. 🔁 块与迭代器演示"
    puts "7. 📁 文件操作演示"
    puts "8. 🎯 综合应用示例"
    puts "9. ❓ 关于系统"
    puts "10. 🚪 退出程序"
    puts "#{'─' * 40}".colorize(:blue)
    print "请选择 (1-10): ".colorize(:yellow)
  end
  
  def display_submenu(title, options)
    clear_screen
    puts "\n🔍 #{title}".colorize(:blue).bold
    puts "#{'─' * 40}".colorize(:blue)
    options.each_with_index do |option, index|
      puts "#{index + 1}. #{option}"
    end
    puts "#{options.size + 1}. 🔙 返回主菜单"
    puts "#{'─' * 40}".colorize(:blue)
    print "请选择 (1-#{options.size + 1}): ".colorize(:yellow)
  end
  
  def get_user_choice(min, max)
    loop do
      choice = gets.chomp.to_i
      return choice if choice.between?(min, max)
      
      print "无效选择，请输入 #{min}-#{max}: ".colorize(:red)
    end
  end
  
  def process_main_choice(choice)
    case choice
    when 1
      show_basics_menu
    when 2
      show_control_structures_demo
    when 3
      show_collections_menu
    when 4
      show_oop_demo
    when 5
      show_modules_demo
    when 6
      show_blocks_demo
    when 7
      show_files_demo
    when 8
      show_comprehensive_demo
    when 9
      show_about_info
    when 10
      @running = false
    end
  end
  
  def show_basics_menu
    options = [
      "📊 变量与数据类型演示",
      "🔍 数据类型检查工具",
      "🎯 综合基础演示"
    ]
    
    loop do
      display_submenu("基础语法演示", options)
      choice = get_user_choice(1, options.size + 1)
      
      case choice
      when 1
        run_demo("变量与数据类型", -> { VariablesDemo.new.run_all_demos })
      when 2
        run_demo("数据类型检查", -> { DataTypeChecker.run_all_demos })
      when 3
        run_demo("综合基础演示") do
          demo = VariablesDemo.new
          demo.demonstrate_variables
          demo.demonstrate_strings
          DataTypeChecker.demonstrate_type_checking
        end
      when options.size + 1
        break
      end
    end
  end
  
  def show_control_structures_demo
    run_demo("控制结构") do
      demo = ControlStructuresDemo.new
      demo.run_all_demos
    end
  end
  
  def show_collections_menu
    options = [
      "🗂️ 数组操作演示",
      "📋 哈希操作演示",
      "🔄 集合转换演示"
    ]
    
    loop do
      display_submenu("集合操作演示", options)
      choice = get_user_choice(1, options.size + 1)
      
      case choice
      when 1
        run_demo("数组操作", -> { ArrayDemo.new.run_all_demos })
      when 2
        run_demo("哈希操作", -> { HashDemo.new.run_all_demos })
      when 3
        run_demo("集合转换", -> { CollectionsUtils.run_interactive_demo })
      when options.size + 1
        break
      end
    end
  end
  
  def show_oop_demo
    run_demo("面向对象编程", -> { OOPDemo.run_all_demos })
  end
  
  def show_modules_demo
    run_demo("模块与混入", -> { ModulesDemo.run_all_demos })
  end
  
  def show_blocks_demo
    run_demo("块与迭代器", -> { BlocksDemo.run_all_demos })
  end
  
  def show_files_demo
    run_demo("文件操作", -> { FilesDemo.run_all_demos })
  end
  
  def show_comprehensive_demo
    run_demo("综合应用示例") do
      puts "🎯 Ruby编程综合应用示例".colorize(:blue).bold
      puts "\n这个示例将展示如何结合使用Ruby的各种特性".colorize(:green)
      
      # 简单的学生管理系统演示
      puts "\n📚 学生管理系统演示:".colorize(:yellow)
      
      # 使用类和模块
      class Student
        attr_accessor :name, :age, :grades
        
        def initialize(name, age)
          @name = name
          @age = age
          @grades = {}
        end
        
        def add_grade(subject, grade)
          @grades[subject] = grade
        end
        
        def average_grade
          return 0 if @grades.empty?
          @grades.values.sum.to_f / @grades.size
        end
        
        def to_s
          "#{@name}(#{@age}岁) - 平均分: #{average_grade.round(1)}"
        end
      end
      
      # 创建学生
      students = []
      students << Student.new("张三", 20)
      students << Student.new("李四", 19)
      students << Student.new("王五", 21)
      
      # 添加成绩
      students[0].add_grade("数学", 95)
      students[0].add_grade("英语", 87)
      students[1].add_grade("数学", 88)
      students[1].add_grade("英语", 92)
      students[2].add_grade("数学", 91)
      students[2].add_grade("英语", 85)
      
      # 使用迭代器展示结果
      puts "\n学生信息:"
      students.each_with_index do |student, index|
        puts "  #{index + 1}. #{student}".colorize(:green)
      end
      
      # 使用集合方法进行统计
      best_student = students.max_by(&:average_grade)
      puts "\n最优秀的学生: #{best_student}".colorize(:blue)
      
      puts "\n这个示例展示了:".colorize(:yellow)
      puts "- 类的定义和使用"
      puts "- 属性访问器"
      puts "- 哈希和数组的使用"
      puts "- 迭代器和块的使用"
      puts "- 方法链和符号转过程"
    end
  end
  
  def show_about_info
    clear_screen
    puts "\n📖 关于Ruby基础教程演示系统".colorize(:blue).bold
    puts "#{'─' * 50}".colorize(:blue)
    puts "版本: 1.0.0".colorize(:green)
    puts "作者: Ruby学习小组".colorize(:green)
    puts "目的: 通过实际代码演示Ruby编程基础".colorize(:green)
    puts "\n🎯 涵盖内容:".colorize(:yellow)
    puts "- Ruby基础语法和数据类型"
    puts "- 控制结构和流程控制"
    puts "- 数组和哈希等集合操作"
    puts "- 面向对象编程特性"
    puts "- 模块和混入机制"
    puts "- 块和迭代器"
    puts "- 文件I/O操作"
    puts "\n💡 使用建议:".colorize(:yellow)
    puts "- 建议按顺序学习各个模块"
    puts "- 可以重复运行演示来加深理解"
    puts "- 尝试修改演示代码进行实验"
    
    puts "\n按回车键返回主菜单...".colorize(:cyan)
    gets
  end
  
  def run_demo(title, demo_proc = nil, &block)
    clear_screen
    puts "\n🚀 正在运行: #{title}".colorize(:blue).bold
    puts "#{'═' * 60}".colorize(:blue)
    
    begin
      if demo_proc
        demo_proc.call
      else
        yield if block_given?
      end
    rescue => e
      puts "\n❌ 演示过程中出现错误: #{e.message}".colorize(:red)
      puts "错误详情: #{e.backtrace.first}".colorize(:red)
    end
    
    puts "\n#{'═' * 60}".colorize(:blue)
    puts "✅ #{title} 演示完成！".colorize(:green).bold
    puts "\n按回车键返回菜单...".colorize(:cyan)
    gets
  end
  
  def clear_screen
    system('clear') || system('cls')
  end
  
  def display_goodbye
    clear_screen
    puts "\n#{'=' * 60}".colorize(:blue)
    puts "#{' ' * 20}👋 感谢使用！".colorize(:green).bold
    puts "#{'=' * 60}".colorize(:blue)
    puts "感谢您使用Ruby基础教程演示系统！".colorize(:green)
    puts "希望这次学习对您有所帮助。".colorize(:green)
    puts "祝您在Ruby编程的道路上越走越远！🚀".colorize(:yellow)
    puts "#{'=' * 60}".colorize(:blue)
  end
end