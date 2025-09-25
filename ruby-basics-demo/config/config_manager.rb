# Ruby配置管理系统
# 管理应用程序的配置参数和显示设置

require 'yaml'
require 'json'

class ConfigManager
  DEFAULT_CONFIG = {
    display: {
      colors: true,
      clear_screen: true,
      show_line_numbers: true,
      pause_after_demo: true,
      theme: 'default'
    },
    demo: {
      auto_run: false,
      show_explanations: true,
      detailed_output: true,
      exercise_mode: false
    },
    system: {
      log_level: 'info',
      auto_save: true,
      backup_config: true
    }
  }.freeze
  
  def initialize(config_file = 'config/settings.yml')
    @config_file = config_file
    @config = load_config
  end
  
  def get(key_path)
    keys = key_path.to_s.split('.')
    result = @config
    
    keys.each do |key|
      result = result[key.to_sym]
      return nil if result.nil?
    end
    
    result
  end
  
  def set(key_path, value)
    keys = key_path.to_s.split('.')
    target = @config
    
    keys[0...-1].each do |key|
      target[key.to_sym] ||= {}
      target = target[key.to_sym]
    end
    
    target[keys.last.to_sym] = value
    save_config if get('system.auto_save')
  end
  
  def colors_enabled?
    get('display.colors')
  end
  
  def should_clear_screen?
    get('display.clear_screen')
  end
  
  def show_line_numbers?
    get('display.show_line_numbers')
  end
  
  def pause_after_demo?
    get('display.pause_after_demo')
  end
  
  def reset_to_defaults
    @config = deep_copy(DEFAULT_CONFIG)
    save_config
  end
  
  def save_config
    ensure_config_directory
    
    begin
      File.open(@config_file, 'w') do |file|
        file.write(YAML.dump(@config))
      end
      true
    rescue => e
      puts "保存配置失败: #{e.message}".colorize(:red)
      false
    end
  end
  
  def display_current_config
    puts "📋 当前配置设置".colorize(:blue).bold
    puts "#{'-' * 40}".colorize(:blue)
    
    @config.each do |category, settings|
      puts "#{category.to_s.capitalize}:".colorize(:yellow)
      settings.each do |key, value|
        puts "  #{key}: #{value}".colorize(:green)
      end
      puts
    end
  end
  
  private
  
  def load_config
    if File.exist?(@config_file)
      begin
        loaded_config = YAML.load_file(@config_file)
        merge_with_defaults(loaded_config)
      rescue => e
        puts "加载配置失败，使用默认配置: #{e.message}".colorize(:yellow)
        deep_copy(DEFAULT_CONFIG)
      end
    else
      puts "配置文件不存在，创建默认配置".colorize(:yellow)
      config = deep_copy(DEFAULT_CONFIG)
      save_config
      config
    end
  end
  
  def merge_with_defaults(loaded_config)
    result = deep_copy(DEFAULT_CONFIG)
    deep_merge!(result, loaded_config || {})
    result
  end
  
  def deep_copy(obj)
    Marshal.load(Marshal.dump(obj))
  end
  
  def deep_merge!(target, source)
    source.each do |key, value|
      key = key.to_sym
      if target[key].is_a?(Hash) && value.is_a?(Hash)
        deep_merge!(target[key], value)
      else
        target[key] = value
      end
    end
    target
  end
  
  def ensure_config_directory
    config_dir = File.dirname(@config_file)
    Dir.mkdir(config_dir) unless Dir.exist?(config_dir)
  end
end

# 全局配置实例
$config = ConfigManager.new