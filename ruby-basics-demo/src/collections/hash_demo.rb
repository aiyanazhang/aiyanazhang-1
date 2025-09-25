# Ruby哈希操作演示模块
# 展示Ruby哈希的创建、操作和常用方法

class HashDemo
  def initialize
    @sample_user = {
      name: 'Alice',
      age: 25,
      email: 'alice@example.com',
      skills: ['Ruby', 'JavaScript', 'Python']
    }
    
    @sample_scores = {
      'Alice' => 95,
      'Bob' => 87,
      'Charlie' => 92,
      'Diana' => 88
    }
  end
  
  # 演示哈希创建和初始化
  def demonstrate_hash_creation
    puts "=== Ruby哈希创建演示 ===\n".colorize(:blue)
    
    # 基本哈希创建
    puts "1. 基本哈希创建方法:".colorize(:yellow)
    
    # 使用大括号
    hash1 = { 'name' => 'Ruby', 'version' => 3.0 }
    puts "   { 'name' => 'Ruby', 'version' => 3.0 }: #{hash1}".colorize(:green)
    
    # 使用符号作为键
    hash2 = { name: 'Ruby', version: 3.0 }
    puts "   { name: 'Ruby', version: 3.0 }: #{hash2}".colorize(:green)
    
    # 使用Hash.new
    hash3 = Hash.new
    hash3['key'] = 'value'
    puts "   Hash.new + 赋值: #{hash3}".colorize(:green)
    
    # 使用Hash[]
    hash4 = Hash['a', 1, 'b', 2, 'c', 3]
    puts "   Hash['a', 1, 'b', 2, 'c', 3]: #{hash4}".colorize(:green)
    
    # 从数组创建哈希
    puts "\n2. 从数组创建哈希:".colorize(:yellow)
    pairs = [['name', 'Ruby'], ['version', 3.0]]
    hash_from_array = Hash[pairs]
    puts "   Hash[#{pairs}]: #{hash_from_array}".colorize(:green)
    
    # 使用zip创建哈希
    keys = ['a', 'b', 'c']
    values = [1, 2, 3]
    zipped_hash = Hash[keys.zip(values)]
    puts "   Hash[keys.zip(values)]: #{zipped_hash}".colorize(:green)
    
    # 设置默认值
    puts "\n3. 设置默认值:".colorize(:yellow)
    hash_with_default = Hash.new(0)  # 默认值为0
    hash_with_default['existing'] = 5
    puts "   Hash.new(0): #{hash_with_default}".colorize(:green)
    puts "   访问不存在的键: #{hash_with_default['nonexistent']}".colorize(:green)
    
    # 使用块设置默认值
    hash_with_block = Hash.new { |hash, key| hash[key] = [] }
    hash_with_block['fruits'] << 'apple'
    puts "   Hash.new { |h, k| h[k] = [] }: #{hash_with_block}".colorize(:green)
    
    # 符号与字符串键的区别
    puts "\n4. 符号与字符串键的区别:".colorize(:yellow)
    mixed_hash = { 'string_key' => 'value1', :symbol_key => 'value2' }
    puts "   混合键类型: #{mixed_hash}".colorize(:green)
    puts "   mixed_hash['string_key']: #{mixed_hash['string_key']}".colorize(:green)
    puts "   mixed_hash[:symbol_key]: #{mixed_hash[:symbol_key]}".colorize(:green)
  end
  
  # 演示哈希访问和修改
  def demonstrate_hash_access
    puts "\n=== Ruby哈希访问和修改演示 ===\n".colorize(:blue)
    
    user = @sample_user.dup
    puts "示例哈希: #{user}".colorize(:cyan)
    
    # 基本访问
    puts "\n1. 基本访问方法:".colorize(:yellow)
    puts "   user[:name]: #{user[:name]}".colorize(:green)
    puts "   user['name']: #{user['name']}".colorize(:green)  # nil，因为键是符号
    puts "   user.fetch(:age): #{user.fetch(:age)}".colorize(:green)
    puts "   user.fetch(:height, '未知'): #{user.fetch(:height, '未知')}".colorize(:green)
    
    # 安全访问
    puts "\n2. 安全访问:".colorize(:yellow)
    puts "   user.dig(:skills, 0): #{user.dig(:skills, 0)}".colorize(:green)
    puts "   user.dig(:address, :city): #{user.dig(:address, :city)}".colorize(:green)
    
    # 检查键是否存在
    puts "\n3. 检查键是否存在:".colorize(:yellow)
    puts "   user.key?(:name): #{user.key?(:name)}".colorize(:green)
    puts "   user.has_key?(:name): #{user.has_key?(:name)}".colorize(:green)
    puts "   user.include?(:name): #{user.include?(:name)}".colorize(:green)
    puts "   user.member?(:height): #{user.member?(:height)}".colorize(:green)
    
    # 检查值是否存在
    puts "\n4. 检查值是否存在:".colorize(:yellow)
    puts "   user.value?('Alice'): #{user.value?('Alice')}".colorize(:green)
    puts "   user.has_value?('Alice'): #{user.has_value?('Alice')}".colorize(:green)
    
    # 修改值
    puts "\n5. 修改值:".colorize(:yellow)
    user[:age] = 26
    puts "   user[:age] = 26: #{user[:age]}".colorize(:green)
    
    user[:city] = 'Beijing'
    puts "   user[:city] = 'Beijing': #{user}".colorize(:green)
    
    # 嵌套修改
    user[:skills] << 'Go'
    puts "   user[:skills] << 'Go': #{user[:skills]}".colorize(:green)
  end
  
  # 演示哈希添加和删除操作
  def demonstrate_hash_modification
    puts "\n=== Ruby哈希添加和删除演示 ===\n".colorize(:blue)
    
    hash = { a: 1, b: 2, c: 3 }
    puts "初始哈希: #{hash}".colorize(:cyan)
    
    # 添加元素
    puts "\n1. 添加元素:".colorize(:yellow)
    hash[:d] = 4
    puts "   hash[:d] = 4: #{hash}".colorize(:green)
    
    hash.store(:e, 5)
    puts "   hash.store(:e, 5): #{hash}".colorize(:green)
    
    # 批量合并
    new_elements = { f: 6, g: 7 }
    hash.merge!(new_elements)
    puts "   hash.merge!(#{new_elements}): #{hash}".colorize(:green)
    
    # update方法（merge!的别名）
    hash.update(h: 8, i: 9)
    puts "   hash.update(h: 8, i: 9): #{hash}".colorize(:green)
    
    # 删除元素
    puts "\n2. 删除元素:".colorize(:yellow)
    deleted_value = hash.delete(:i)
    puts "   delete(:i): #{deleted_value}, 哈希: #{hash}".colorize(:green)
    
    # 条件删除
    hash.delete_if { |key, value| value > 7 }
    puts "   delete_if { |k, v| v > 7 }: #{hash}".colorize(:green)
    
    # 保留满足条件的元素
    hash.keep_if { |key, value| value <= 5 }
    puts "   keep_if { |k, v| v <= 5 }: #{hash}".colorize(:green)
    
    # 清空哈希
    empty_hash = { x: 1, y: 2 }
    puts "   清空前: #{empty_hash}".colorize(:cyan)
    empty_hash.clear
    puts "   clear后: #{empty_hash}".colorize(:green)
    
    # 使用reject创建新哈希
    puts "\n3. 过滤操作:".colorize(:yellow)
    original = { a: 1, b: 2, c: 3, d: 4, e: 5 }
    puts "   原哈希: #{original}".colorize(:cyan)
    
    even_values = original.select { |k, v| v.even? }
    puts "   select { |k, v| v.even? }: #{even_values}".colorize(:green)
    
    odd_values = original.reject { |k, v| v.even? }
    puts "   reject { |k, v| v.even? }: #{odd_values}".colorize(:green)
  end
  
  # 演示哈希遍历方法
  def demonstrate_hash_iteration
    puts "\n=== Ruby哈希遍历演示 ===\n".colorize(:blue)
    
    scores = @sample_scores.dup
    puts "示例哈希: #{scores}".colorize(:cyan)
    
    # 遍历键值对
    puts "\n1. 遍历键值对:".colorize(:yellow)
    puts "   each方法:"
    scores.each { |name, score| puts "     #{name}: #{score}分".colorize(:green) }
    
    puts "\n   each_pair方法:"
    scores.each_pair { |name, score| puts "     #{name}获得#{score}分".colorize(:green) }
    
    # 遍历键
    puts "\n2. 遍历键:".colorize(:yellow)
    puts "   each_key方法:"
    scores.each_key { |name| puts "     学生: #{name}".colorize(:green) }
    
    # 遍历值
    puts "\n3. 遍历值:".colorize(:yellow)
    puts "   each_value方法:"
    scores.each_value { |score| puts "     分数: #{score}".colorize(:green) }
    
    # 带索引遍历
    puts "\n4. 带索引遍历:".colorize(:yellow)
    puts "   each_with_index方法:"
    scores.each_with_index do |(name, score), index|
      puts "     第#{index + 1}名: #{name} - #{score}分".colorize(:green)
    end
    
    # map操作
    puts "\n5. map变换:".colorize(:yellow)
    grade_map = scores.map { |name, score| [name, score >= 90 ? 'A' : 'B'] }
    puts "   map { |name, score| [name, score >= 90 ? 'A' : 'B'] }:"
    puts "     #{Hash[grade_map]}".colorize(:green)
    
    # transform_values
    puts "\n6. transform_values (Ruby 2.4+):".colorize(:yellow)
    percentage = scores.transform_values { |score| "#{score}%" }
    puts "   transform_values { |score| '\#{score}%' }: #{percentage}".colorize(:green)
    
    # transform_keys
    puts "\n7. transform_keys (Ruby 2.5+):".colorize(:yellow)
    uppercase_keys = scores.transform_keys(&:upcase)
    puts "   transform_keys(&:upcase): #{uppercase_keys}".colorize(:green)
  end
  
  # 演示哈希查找和过滤
  def demonstrate_hash_search_filter
    puts "\n=== Ruby哈希查找和过滤演示 ===\n".colorize(:blue)
    
    users = {
      alice: { age: 25, city: 'Beijing', skills: ['Ruby', 'JavaScript'] },
      bob: { age: 30, city: 'Shanghai', skills: ['Python', 'Go'] },
      charlie: { age: 28, city: 'Beijing', skills: ['Java', 'Ruby'] }
    }
    puts "示例哈希: #{users}".colorize(:cyan)
    
    # 查找单个元素
    puts "\n1. 查找单个元素:".colorize(:yellow)
    ruby_user = users.find { |name, info| info[:skills].include?('Ruby') }
    puts "   find { |name, info| info[:skills].include?('Ruby') }:"
    puts "     #{ruby_user}".colorize(:green)
    
    beijing_user = users.detect { |name, info| info[:city] == 'Beijing' }
    puts "   detect { |name, info| info[:city] == 'Beijing' }:"
    puts "     #{beijing_user}".colorize(:green)
    
    # 过滤元素
    puts "\n2. 过滤元素:".colorize(:yellow)
    young_users = users.select { |name, info| info[:age] < 30 }
    puts "   select { |name, info| info[:age] < 30 }:"
    puts "     #{young_users}".colorize(:green)
    
    non_beijing = users.reject { |name, info| info[:city] == 'Beijing' }
    puts "   reject { |name, info| info[:city] == 'Beijing' }:"
    puts "     #{non_beijing}".colorize(:green)
    
    # 条件检查
    puts "\n3. 条件检查:".colorize(:yellow)
    all_adults = users.all? { |name, info| info[:age] >= 18 }
    puts "   all? { |name, info| info[:age] >= 18 }: #{all_adults}".colorize(:green)
    
    any_old = users.any? { |name, info| info[:age] > 35 }
    puts "   any? { |name, info| info[:age] > 35 }: #{any_old}".colorize(:green)
    
    none_minor = users.none? { |name, info| info[:age] < 18 }
    puts "   none? { |name, info| info[:age] < 18 }: #{none_minor}".colorize(:green)
    
    # 计数
    puts "\n4. 计数操作:".colorize(:yellow)
    beijing_count = users.count { |name, info| info[:city] == 'Beijing' }
    puts "   count { |name, info| info[:city] == 'Beijing' }: #{beijing_count}".colorize(:green)
    
    # 分组
    puts "\n5. 分组操作:".colorize(:yellow)
    by_city = users.group_by { |name, info| info[:city] }
    puts "   group_by { |name, info| info[:city] }:"
    by_city.each { |city, users_in_city| puts "     #{city}: #{users_in_city.map(&:first)}".colorize(:green) }
  end
  
  # 演示哈希合并和转换
  def demonstrate_hash_merge_conversion
    puts "\n=== Ruby哈希合并和转换演示 ===\n".colorize(:blue)
    
    # 哈希合并
    puts "1. 哈希合并:".colorize(:yellow)
    hash1 = { a: 1, b: 2 }
    hash2 = { b: 3, c: 4 }
    puts "   hash1: #{hash1}".colorize(:cyan)
    puts "   hash2: #{hash2}".colorize(:cyan)
    
    merged = hash1.merge(hash2)
    puts "   merge: #{merged}".colorize(:green)
    
    # 合并时自定义冲突处理
    custom_merge = hash1.merge(hash2) { |key, old_val, new_val| old_val + new_val }
    puts "   merge with block: #{custom_merge}".colorize(:green)
    
    # 深度合并示例
    puts "\n2. 深度合并:".colorize(:yellow)
    config1 = { database: { host: 'localhost', port: 5432 }, cache: true }
    config2 = { database: { user: 'admin' }, logging: true }
    puts "   config1: #{config1}".colorize(:cyan)
    puts "   config2: #{config2}".colorize(:cyan)
    
    # 简单合并（会覆盖整个database哈希）
    simple_merge = config1.merge(config2)
    puts "   简单合并: #{simple_merge}".colorize(:green)
    
    # 手动深度合并
    def deep_merge(hash1, hash2)
      hash1.merge(hash2) do |key, old_val, new_val|
        old_val.is_a?(Hash) && new_val.is_a?(Hash) ? deep_merge(old_val, new_val) : new_val
      end
    end
    
    deep_merged = deep_merge(config1, config2)
    puts "   深度合并: #{deep_merged}".colorize(:green)
    
    # 哈希转换
    puts "\n3. 哈希转换:".colorize(:yellow)
    hash = { name: 'Ruby', version: 3.0, active: true }
    puts "   原哈希: #{hash}".colorize(:cyan)
    
    # 转换为数组
    array = hash.to_a
    puts "   to_a: #{array}".colorize(:green)
    
    # 获取键和值
    keys = hash.keys
    values = hash.values
    puts "   keys: #{keys}".colorize(:green)
    puts "   values: #{values}".colorize(:green)
    
    # 反转键值
    inverted = hash.invert
    puts "   invert: #{inverted}".colorize(:green)
    
    # 转换为字符串
    puts "\n4. 哈希与字符串转换:".colorize(:yellow)
    string_repr = hash.to_s
    puts "   to_s: #{string_repr}".colorize(:green)
    
    # 转换为JSON格式字符串（需要require 'json'）
    begin
      require 'json'
      json_string = hash.to_json
      puts "   to_json: #{json_string}".colorize(:green)
    rescue LoadError
      puts "   JSON gem 未安装".colorize(:red)
    end
    
    # 从查询字符串创建哈希
    puts "\n5. URL查询参数风格:".colorize(:yellow)
    query_style = hash.map { |k, v| "#{k}=#{v}" }.join('&')
    puts "   查询字符串风格: #{query_style}".colorize(:green)
  end
  
  # 演示哈希的高级特性
  def demonstrate_advanced_features
    puts "\n=== Ruby哈希高级特性演示 ===\n".colorize(:blue)
    
    # 哈希作为方法参数
    puts "1. 哈希作为方法参数:".colorize(:yellow)
    def create_user(name:, age:, email: nil, **options)
      user = { name: name, age: age }
      user[:email] = email if email
      user.merge(options)
    end
    
    user1 = create_user(name: 'Alice', age: 25)
    user2 = create_user(name: 'Bob', age: 30, email: 'bob@example.com', city: 'Shanghai')
    puts "   create_user(name: 'Alice', age: 25): #{user1}".colorize(:green)
    puts "   create_user(name: 'Bob', age: 30, email: 'bob@example.com', city: 'Shanghai'):"
    puts "     #{user2}".colorize(:green)
    
    # 哈希解构
    puts "\n2. 哈希解构:".colorize(:yellow)
    person = { name: 'Charlie', age: 28, city: 'Beijing' }
    name, age = person.values_at(:name, :age)
    puts "   name, age = person.values_at(:name, :age):"
    puts "     name: #{name}, age: #{age}".colorize(:green)
    
    # 使用fetch_values
    name, age, height = person.fetch_values(:name, :age, :height) { |key| "未知#{key}" }
    puts "   fetch_values(:name, :age, :height) { |key| '未知\#{key}' }:"
    puts "     name: #{name}, age: #{age}, height: #{height}".colorize(:green)
    
    # 哈希比较
    puts "\n3. 哈希比较:".colorize(:yellow)
    hash_a = { a: 1, b: 2 }
    hash_b = { b: 2, a: 1 }  # 顺序不同
    hash_c = { a: 1, b: 3 }
    puts "   hash_a: #{hash_a}".colorize(:cyan)
    puts "   hash_b: #{hash_b}".colorize(:cyan)
    puts "   hash_c: #{hash_c}".colorize(:cyan)
    puts "   hash_a == hash_b: #{hash_a == hash_b}".colorize(:green)
    puts "   hash_a == hash_c: #{hash_a == hash_c}".colorize(:green)
    
    # 哈希的嵌套访问
    puts "\n4. 嵌套哈希访问:".colorize(:yellow)
    nested = {
      user: {
        profile: {
          name: 'Alice',
          contact: {
            email: 'alice@example.com',
            phone: '123-456-7890'
          }
        }
      }
    }
    
    puts "   嵌套哈希: #{nested}".colorize(:cyan)
    puts "   dig(:user, :profile, :name): #{nested.dig(:user, :profile, :name)}".colorize(:green)
    puts "   dig(:user, :profile, :contact, :email): #{nested.dig(:user, :profile, :contact, :email)}".colorize(:green)
    puts "   dig(:user, :settings, :theme): #{nested.dig(:user, :settings, :theme)}".colorize(:green)
    
    # 哈希的冻结
    puts "\n5. 哈希冻结:".colorize(:yellow)
    mutable_hash = { a: 1, b: 2 }
    frozen_hash = mutable_hash.freeze
    puts "   frozen_hash.frozen?: #{frozen_hash.frozen?}".colorize(:green)
    
    begin
      frozen_hash[:c] = 3
    rescue FrozenError => e
      puts "   尝试修改冻结哈希: #{e.message}".colorize(:red)
    end
    
    # 默认值的高级用法
    puts "\n6. 默认值的高级用法:".colorize(:yellow)
    word_count = Hash.new(0)
    sentence = "ruby is awesome ruby rocks"
    sentence.split.each { |word| word_count[word] += 1 }
    puts "   单词计数: #{word_count}".colorize(:green)
    
    # 使用default_proc
    nested_hash = Hash.new { |h, k| h[k] = Hash.new(0) }
    nested_hash['fruits']['apple'] += 1
    nested_hash['fruits']['banana'] += 2
    nested_hash['vegetables']['carrot'] += 1
    puts "   嵌套计数: #{nested_hash}".colorize(:green)
  end
  
  # 运行所有演示
  def run_all_demos
    demonstrate_hash_creation
    demonstrate_hash_access
    demonstrate_hash_modification
    demonstrate_hash_iteration
    demonstrate_hash_search_filter
    demonstrate_hash_merge_conversion
    demonstrate_advanced_features
  end
end