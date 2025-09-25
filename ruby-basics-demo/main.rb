#!/usr/bin/env ruby
# Ruby基础教程演示系统 - 主程序入口
# 
# 使用方法:
#   ruby main.rb              # 启动交互式菜单
#   ruby main.rb --demo all   # 运行所有演示
#   ruby main.rb --help       # 显示帮助信息

require_relative 'config/config_manager'
require_relative 'src/menu_system'

class RubyBasicsDemo
  def initialize
    @config = $config
  end
  
  def run(args = ARGV)
    setup_environment
    
    case args.first
    when '--help', '-h'
      show_help
    when '--demo'
      run_demo_mode(args[1])
    when '--version', '-v'
      show_version
    when '--config'
      show_config_menu
    else
      run_interactive_mode
    end
  rescue Interrupt
    puts "\n\n👋 程序被用户中断，再见！".colorize(:yellow)
    exit(0)
  rescue => e
    puts "\n❌ 程序运行出错: #{e.message}".colorize(:red)
    puts "请检查Ruby版本是否为3.0+，并确保所有依赖已安装。".colorize(:yellow)
    exit(1)
  end
  
  private
  
  def setup_environment
    # 检查Ruby版本
    unless RUBY_VERSION >= '3.0.0'
      puts "⚠️  警告: 推荐使用Ruby 3.0或更高版本".colorize(:yellow)
    end
    
    # 尝试加载colorize gem
    begin
      require 'colorize'
    rescue LoadError
      puts "⚠️  colorize gem未安装，将使用无色彩输出"
      # 定义空的colorize方法作为回退
      class String
        def colorize(color)
          self
        end
        
        def bold
          self
        end
      end
    end
  end
  
  def run_interactive_mode
    puts "🚀 启动交互式模式...".colorize(:green)
    menu = MenuSystem.new
    menu.start
  end
  
  def run_demo_mode(demo_type)
    puts "🎯 运行演示模式: #{demo_type}".colorize(:blue)
    
    case demo_type
    when 'all'
      run_all_demos
    when 'basics'
      run_basics_demos
    when 'oop'
      run_oop_demos
    when 'collections'
      run_collections_demos
    else
      puts "❌ 未知的演示类型: #{demo_type}".colorize(:red)
      show_demo_help
    end
  end
  
  def run_all_demos
    puts "📚 运行所有演示模块...".colorize(:blue).bold
    
    demos = [
      ['基础语法', -> { run_basics_demos }],
      ['控制结构', -> { ControlStructuresDemo.new.run_all_demos }],
      ['集合操作', -> { run_collections_demos }],
      ['面向对象', -> { OOPDemo.run_all_demos }],
      ['模块混入', -> { ModulesDemo.run_all_demos }],
      ['块迭代器', -> { BlocksDemo.run_all_demos }],
      ['文件操作', -> { FilesDemo.run_all_demos }]
    ]
    
    demos.each_with_index do |(name, demo_proc), index|
      puts "\n#{'=' * 60}".colorize(:blue)
      puts "#{index + 1}/#{demos.size}. 正在运行: #{name}".colorize(:yellow).bold
      puts "#{'=' * 60}".colorize(:blue)
      
      begin
        demo_proc.call
        puts "\n✅ #{name} 演示完成".colorize(:green)
      rescue => e
        puts "\n❌ #{name} 演示出错: #{e.message}".colorize(:red)
      end
      
      sleep(2) if @config.pause_after_demo?
    end
    
    puts "\n🎉 所有演示运行完成！".colorize(:green).bold
  end
  
  def run_basics_demos
    puts "📝 运行基础语法演示...".colorize(:blue)
    VariablesDemo.new.run_all_demos
    DataTypeChecker.run_all_demos
  end
  
  def run_oop_demos
    puts "🏗️ 运行面向对象演示...".colorize(:blue)
    OOPDemo.run_all_demos
  end
  
  def run_collections_demos
    puts "📊 运行集合操作演示...".colorize(:blue)
    ArrayDemo.new.run_all_demos
    HashDemo.new.run_all_demos
  end
  
  def show_config_menu
    puts "⚙️  配置管理".colorize(:blue).bold
    @config.display_current_config
    
    puts "是否要重置为默认配置? (y/N)".colorize(:yellow)
    response = gets.chomp.downcase
    
    if response == 'y' || response == 'yes'
      @config.reset_to_defaults
      puts "✅ 配置已重置为默认值".colorize(:green)
    end
  end
  
  def show_help
    puts <<~HELP
      🎯 Ruby基础教程演示系统
      
      用法:
        ruby main.rb [选项]
      
      选项:
        --help, -h          显示此帮助信息
        --version, -v       显示版本信息
        --demo all          运行所有演示
        --demo basics       运行基础语法演示
        --demo oop          运行面向对象演示
        --demo collections  运行集合操作演示
        --config            配置管理
      
      示例:
        ruby main.rb                    # 启动交互式菜单
        ruby main.rb --demo all         # 运行所有演示
        ruby main.rb --demo basics      # 只运行基础演示
      
      📚 更多信息请访问项目文档。
    HELP
  end
  
  def show_demo_help
    puts <<~DEMO_HELP
      🎯 可用的演示类型:
      
        all         - 运行所有演示模块
        basics      - 基础语法和数据类型
        oop         - 面向对象编程
        collections - 数组和哈希操作
        modules     - 模块和混入
        blocks      - 块和迭代器
        files       - 文件I/O操作
      
      示例: ruby main.rb --demo basics
    DEMO_HELP
  end
  
  def show_version
    puts <<~VERSION
      🎯 Ruby基础教程演示系统
      
      版本: 1.0.0
      Ruby版本: #{RUBY_VERSION}
      平台: #{RUBY_PLATFORM}
      
      © 2024 Ruby学习小组
    VERSION
  end
end

# 程序入口点
if __FILE__ == $0
  app = RubyBasicsDemo.new
  app.run
end