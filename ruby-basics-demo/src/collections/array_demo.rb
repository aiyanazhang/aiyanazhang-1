# Ruby数组操作演示模块
# 展示Ruby数组的创建、操作和常用方法

class ArrayDemo
  def initialize
    @sample_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    @sample_fruits = ['苹果', '香蕉', '橙子', '葡萄', '草莓']
    @mixed_array = [1, 'hello', :symbol, [1, 2], { key: 'value' }]
  end
  
  # 演示数组创建和初始化
  def demonstrate_array_creation
    puts "=== Ruby数组创建演示 ===\n".colorize(:blue)
    
    # 基本数组创建
    puts "1. 基本数组创建方法:".colorize(:yellow)
    array1 = [1, 2, 3, 4, 5]
    array2 = Array.new(5, 0)  # 创建5个元素都是0的数组
    array3 = Array.new(3) { |i| i * 2 }  # 使用块创建数组
    
    puts "   字面量创建: #{array1}".colorize(:green)
    puts "   Array.new(5, 0): #{array2}".colorize(:green)
    puts "   Array.new(3) { |i| i * 2 }: #{array3}".colorize(:green)
    
    # 范围转数组
    puts "\n2. 范围转换为数组:".colorize(:yellow)
    range_array = (1..5).to_a
    char_array = ('a'..'e').to_a
    puts "   (1..5).to_a: #{range_array}".colorize(:green)
    puts "   ('a'..'e').to_a: #{char_array}".colorize(:green)
    
    # 字符串分割为数组
    puts "\n3. 字符串分割为数组:".colorize(:yellow)
    string_array = "apple,banana,orange".split(',')
    word_array = "hello world ruby".split
    puts "   'apple,banana,orange'.split(','): #{string_array}".colorize(:green)
    puts "   'hello world ruby'.split: #{word_array}".colorize(:green)
    
    # %w和%W语法
    puts "\n4. %w和%W快捷语法:".colorize(:yellow)
    w_array = %w[red green blue yellow]
    name = "Ruby"
    big_w_array = %W[hello #{name} world]  # 支持插值
    puts "   %w[red green blue yellow]: #{w_array}".colorize(:green)
    puts "   %W[hello \#{name} world]: #{big_w_array}".colorize(:green)
    
    # 多维数组
    puts "\n5. 多维数组:".colorize(:yellow)
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    puts "   二维数组: #{matrix}".colorize(:green)
    puts "   访问元素 matrix[1][2]: #{matrix[1][2]}".colorize(:green)
    
    # 数组解构
    puts "\n6. 数组解构赋值:".colorize(:yellow)
    first, second, *rest = [1, 2, 3, 4, 5]
    puts "   first, second, *rest = [1, 2, 3, 4, 5]".colorize(:green)
    puts "   first: #{first}, second: #{second}, rest: #{rest}".colorize(:green)
  end
  
  # 演示数组访问和修改
  def demonstrate_array_access
    puts "\n=== Ruby数组访问和修改演示 ===\n".colorize(:blue)
    
    array = @sample_fruits.dup
    puts "示例数组: #{array}".colorize(:cyan)
    
    # 基本访问
    puts "\n1. 基本访问方法:".colorize(:yellow)
    puts "   array[0]: #{array[0]}".colorize(:green)
    puts "   array[-1]: #{array[-1]}".colorize(:green)  # 最后一个元素
    puts "   array.first: #{array.first}".colorize(:green)
    puts "   array.last: #{array.last}".colorize(:green)
    
    # 切片访问
    puts "\n2. 切片访问:".colorize(:yellow)
    puts "   array[1, 2]: #{array[1, 2]}".colorize(:green)  # 从索引1开始，取2个元素
    puts "   array[1..3]: #{array[1..3]}".colorize(:green)  # 范围访问
    puts "   array[1...3]: #{array[1...3]}".colorize(:green)  # 排除最后一个
    
    # 安全访问
    puts "\n3. 安全访问:".colorize(:yellow)
    puts "   array.fetch(10, '默认值'): #{array.fetch(10, '默认值')}".colorize(:green)
    puts "   array.dig(2): #{array.dig(2)}".colorize(:green)
    
    # 修改元素
    puts "\n4. 修改元素:".colorize(:yellow)
    array[0] = '红苹果'
    puts "   array[0] = '红苹果': #{array}".colorize(:green)
    
    array[1, 2] = ['黄香蕉', '橙橙子']  # 替换多个元素
    puts "   array[1, 2] = ['黄香蕉', '橙橙子']: #{array}".colorize(:green)
    
    # 使用负索引修改
    array[-1] = '新草莓'
    puts "   array[-1] = '新草莓': #{array}".colorize(:green)
  end
  
  # 演示数组添加和删除操作
  def demonstrate_array_modification
    puts "\n=== Ruby数组添加和删除演示 ===\n".colorize(:blue)
    
    array = [1, 2, 3]
    puts "初始数组: #{array}".colorize(:cyan)
    
    # 添加元素
    puts "\n1. 添加元素:".colorize(:yellow)
    array.push(4)
    puts "   push(4): #{array}".colorize(:green)
    
    array << 5
    puts "   << 5: #{array}".colorize(:green)
    
    array.unshift(0)
    puts "   unshift(0): #{array}".colorize(:green)
    
    array.insert(3, 2.5)
    puts "   insert(3, 2.5): #{array}".colorize(:green)
    
    # 删除元素
    puts "\n2. 删除元素:".colorize(:yellow)
    last_element = array.pop
    puts "   pop: #{last_element}, 数组: #{array}".colorize(:green)
    
    first_element = array.shift
    puts "   shift: #{first_element}, 数组: #{array}".colorize(:green)
    
    deleted_element = array.delete_at(2)
    puts "   delete_at(2): #{deleted_element}, 数组: #{array}".colorize(:green)
    
    array.delete(2.5)
    puts "   delete(2.5): #{array}".colorize(:green)
    
    # 数组合并
    puts "\n3. 数组合并:".colorize(:yellow)
    array1 = [1, 2, 3]
    array2 = [4, 5, 6]
    puts "   array1: #{array1}, array2: #{array2}".colorize(:cyan)
    puts "   array1 + array2: #{array1 + array2}".colorize(:green)
    puts "   array1.concat(array2): #{array1.concat(array2.dup)}".colorize(:green)
    
    # 数组运算
    puts "\n4. 数组运算:".colorize(:yellow)
    set1 = [1, 2, 3, 4]
    set2 = [3, 4, 5, 6]
    puts "   set1: #{set1}, set2: #{set2}".colorize(:cyan)
    puts "   交集 (set1 & set2): #{set1 & set2}".colorize(:green)
    puts "   并集 (set1 | set2): #{set1 | set2}".colorize(:green)
    puts "   差集 (set1 - set2): #{set1 - set2}".colorize(:green)
    
    # 数组去重和排序
    puts "\n5. 数组去重和排序:".colorize(:yellow)
    duplicate_array = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    puts "   原数组: #{duplicate_array}".colorize(:cyan)
    puts "   去重 uniq: #{duplicate_array.uniq}".colorize(:green)
    puts "   排序 sort: #{duplicate_array.sort}".colorize(:green)
    puts "   逆序 reverse: #{duplicate_array.reverse}".colorize(:green)
    puts "   随机排序 shuffle: #{duplicate_array.shuffle}".colorize(:green)
  end
  
  # 演示数组查找和过滤
  def demonstrate_array_search_filter
    puts "\n=== Ruby数组查找和过滤演示 ===\n".colorize(:blue)
    
    numbers = @sample_numbers
    puts "示例数组: #{numbers}".colorize(:cyan)
    
    # 查找元素
    puts "\n1. 查找元素:".colorize(:yellow)
    puts "   include?(5): #{numbers.include?(5)}".colorize(:green)
    puts "   index(5): #{numbers.index(5)}".colorize(:green)
    puts "   find_index { |n| n > 5 }: #{numbers.find_index { |n| n > 5 }}".colorize(:green)
    puts "   count(5): #{numbers.count(5)}".colorize(:green)
    puts "   count { |n| n.even? }: #{numbers.count { |n| n.even? }}".colorize(:green)
    
    # 过滤元素
    puts "\n2. 过滤元素:".colorize(:yellow)
    even_numbers = numbers.select { |n| n.even? }
    puts "   select { |n| n.even? }: #{even_numbers}".colorize(:green)
    
    odd_numbers = numbers.reject { |n| n.even? }
    puts "   reject { |n| n.even? }: #{odd_numbers}".colorize(:green)
    
    small_numbers = numbers.take_while { |n| n < 6 }
    puts "   take_while { |n| n < 6 }: #{small_numbers}".colorize(:green)
    
    after_five = numbers.drop_while { |n| n <= 5 }
    puts "   drop_while { |n| n <= 5 }: #{after_five}".colorize(:green)
    
    # 查找单个元素
    puts "\n3. 查找单个元素:".colorize(:yellow)
    first_even = numbers.find { |n| n.even? }
    puts "   find { |n| n.even? }: #{first_even}".colorize(:green)
    
    first_big = numbers.detect { |n| n > 8 }
    puts "   detect { |n| n > 8 }: #{first_big}".colorize(:green)
    
    # 条件检查
    puts "\n4. 条件检查:".colorize(:yellow)
    puts "   all? { |n| n > 0 }: #{numbers.all? { |n| n > 0 }}".colorize(:green)
    puts "   any? { |n| n > 5 }: #{numbers.any? { |n| n > 5 }}".colorize(:green)
    puts "   none? { |n| n > 10 }: #{numbers.none? { |n| n > 10 }}".colorize(:green)
    puts "   one? { |n| n == 5 }: #{numbers.one? { |n| n == 5 }}".colorize(:green)
    
    # 分区
    puts "\n5. 分区操作:".colorize(:yellow)
    even_odd = numbers.partition { |n| n.even? }
    puts "   partition { |n| n.even? }: #{even_odd}".colorize(:green)
    
    grouped = numbers.group_by { |n| n.even? ? 'even' : 'odd' }
    puts "   group_by { |n| n.even? ? 'even' : 'odd' }: #{grouped}".colorize(:green)
  end
  
  # 演示数组变换操作
  def demonstrate_array_transformation
    puts "\n=== Ruby数组变换演示 ===\n".colorize(:blue)
    
    numbers = (1..5).to_a
    puts "示例数组: #{numbers}".colorize(:cyan)
    
    # map操作
    puts "\n1. map变换:".colorize(:yellow)
    squared = numbers.map { |n| n ** 2 }
    puts "   map { |n| n ** 2 }: #{squared}".colorize(:green)
    
    strings = numbers.collect { |n| "数字#{n}" }
    puts "   collect { |n| '数字\#{n}' }: #{strings}".colorize(:green)
    
    # 就地修改
    original = numbers.dup
    original.map! { |n| n * 10 }
    puts "   map! { |n| n * 10 }: #{original}".colorize(:green)
    
    # 扁平化
    puts "\n2. 扁平化操作:".colorize(:yellow)
    nested = [[1, 2], [3, [4, 5]], [6, 7]]
    puts "   原数组: #{nested}".colorize(:cyan)
    puts "   flatten: #{nested.flatten}".colorize(:green)
    puts "   flatten(1): #{nested.flatten(1)}".colorize(:green)
    
    # 压缩操作
    puts "\n3. 压缩操作:".colorize(:yellow)
    array_with_nil = [1, nil, 2, nil, 3]
    puts "   原数组: #{array_with_nil}".colorize(:cyan)
    puts "   compact: #{array_with_nil.compact}".colorize(:green)
    
    # zip操作
    puts "\n4. zip组合:".colorize(:yellow)
    names = ['Alice', 'Bob', 'Charlie']
    ages = [25, 30, 35]
    puts "   names: #{names}".colorize(:cyan)
    puts "   ages: #{ages}".colorize(:cyan)
    puts "   names.zip(ages): #{names.zip(ages)}".colorize(:green)
    
    # 转置
    puts "\n5. 转置操作:".colorize(:yellow)
    matrix = [[1, 2, 3], [4, 5, 6]]
    puts "   原矩阵: #{matrix}".colorize(:cyan)
    puts "   transpose: #{matrix.transpose}".colorize(:green)
    
    # reduce/inject聚合操作
    puts "\n6. reduce/inject聚合:".colorize(:yellow)
    sum = numbers.reduce(0) { |acc, n| acc + n }
    puts "   reduce(0) { |acc, n| acc + n }: #{sum}".colorize(:green)
    
    product = numbers.inject(1, :*)
    puts "   inject(1, :*): #{product}".colorize(:green)
    
    max = numbers.reduce { |acc, n| acc > n ? acc : n }
    puts "   reduce { |acc, n| acc > n ? acc : n }: #{max}".colorize(:green)
  end
  
  # 演示数组的高级特性
  def demonstrate_advanced_features
    puts "\n=== Ruby数组高级特性演示 ===\n".colorize(:blue)
    
    # 数组作为栈
    puts "1. 数组作为栈(LIFO):".colorize(:yellow)
    stack = []
    stack.push(1, 2, 3)
    puts "   push(1, 2, 3): #{stack}".colorize(:green)
    puts "   pop: #{stack.pop}, 栈: #{stack}".colorize(:green)
    puts "   pop: #{stack.pop}, 栈: #{stack}".colorize(:green)
    
    # 数组作为队列
    puts "\n2. 数组作为队列(FIFO):".colorize(:yellow)
    queue = []
    queue.push(1, 2, 3)
    puts "   push(1, 2, 3): #{queue}".colorize(:green)
    puts "   shift: #{queue.shift}, 队列: #{queue}".colorize(:green)
    puts "   shift: #{queue.shift}, 队列: #{queue}".colorize(:green)
    
    # 数组切片和范围
    puts "\n3. 数组切片技巧:".colorize(:yellow)
    array = (1..10).to_a
    puts "   原数组: #{array}".colorize(:cyan)
    puts "   取前3个: #{array.take(3)}".colorize(:green)
    puts "   跳过前3个: #{array.drop(3)}".colorize(:green)
    puts "   最后3个: #{array.last(3)}".colorize(:green)
    puts "   除了最后3个: #{array[0...-3]}".colorize(:green)
    
    # 数组字符串转换
    puts "\n4. 数组与字符串转换:".colorize(:yellow)
    words = %w[Ruby is awesome]
    puts "   数组: #{words}".colorize(:cyan)
    puts "   join(' '): '#{words.join(' ')}'".colorize(:green)
    puts "   join(', '): '#{words.join(', ')}'".colorize(:green)
    puts "   join: '#{words.join}'".colorize(:green)
    
    # 数组比较
    puts "\n5. 数组比较:".colorize(:yellow)
    array1 = [1, 2, 3]
    array2 = [1, 2, 3]
    array3 = [3, 2, 1]
    puts "   array1: #{array1}".colorize(:cyan)
    puts "   array2: #{array2}".colorize(:cyan)
    puts "   array3: #{array3}".colorize(:cyan)
    puts "   array1 == array2: #{array1 == array2}".colorize(:green)
    puts "   array1 == array3: #{array1 == array3}".colorize(:green)
    puts "   array1 <=> array3: #{array1 <=> array3}".colorize(:green)
    
    # 数组性能提示
    puts "\n6. 性能提示:".colorize(:yellow)
    puts "   - 使用 << 比 push 稍快".colorize(:green)
    puts "   - 从尾部删除(pop)比从头部删除(shift)快".colorize(:green)
    puts "   - 预分配大小: Array.new(size)".colorize(:green)
    puts "   - 使用 freeze 防止意外修改".colorize(:green)
    
    frozen_array = [1, 2, 3].freeze
    puts "   frozen_array.frozen?: #{frozen_array.frozen?}".colorize(:green)
  end
  
  # 运行所有演示
  def run_all_demos
    demonstrate_array_creation
    demonstrate_array_access
    demonstrate_array_modification
    demonstrate_array_search_filter
    demonstrate_array_transformation
    demonstrate_advanced_features
  end
end