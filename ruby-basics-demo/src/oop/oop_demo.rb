# Ruby面向对象编程演示模块
# 展示Ruby的类、对象、继承、多态等面向对象特性

# 基本的Person类演示
class Person
  # 类变量
  @@population = 0
  
  # 类常量
  SPECIES = "Homo sapiens"
  
  # attr_* 方法演示
  attr_reader :name, :birth_year    # 只读属性
  attr_writer :nickname             # 只写属性
  attr_accessor :email, :phone      # 读写属性
  
  def initialize(name, birth_year, email = nil)
    @name = name                    # 实例变量
    @birth_year = birth_year
    @email = email
    @@population += 1
    
    puts "创建了新的Person: #{@name}".colorize(:green)
  end
  
  # 实例方法
  def age
    current_year = Time.now.year
    current_year - @birth_year
  end
  
  def introduce
    "你好，我是#{@name}，今年#{age}岁"
  end
  
  def adult?
    age >= 18
  end
  
  # 私有方法演示
  private
  
  def calculate_birth_decade
    (@birth_year / 10) * 10
  end
  
  # 受保护方法演示
  protected
  
  def birth_decade
    "#{calculate_birth_decade}年代"
  end
  
  # 类方法
  def self.population
    @@population
  end
  
  def self.create_anonymous
    new("匿名", 1990)
  end
  
  # 重写to_s方法
  def to_s
    "Person(name: #{@name}, age: #{age})"
  end
  
  # 重写inspect方法
  def inspect
    "#<Person:#{object_id} @name=\"#{@name}\" @birth_year=#{@birth_year}>"
  end
end

# 继承演示 - Student类继承Person类
class Student < Person
  attr_accessor :student_id, :major, :gpa
  
  def initialize(name, birth_year, student_id, major, email = nil)
    super(name, birth_year, email)  # 调用父类的初始化方法
    @student_id = student_id
    @major = major
    @gpa = 0.0
    
    puts "创建了新的Student: #{@name}，专业: #{@major}".colorize(:blue)
  end
  
  # 重写父类方法
  def introduce
    super + "，我是#{@major}专业的学生，学号：#{@student_id}"
  end
  
  # 学生特有的方法
  def study(course)
    puts "#{@name}正在学习#{course}"
  end
  
  def graduate?
    @gpa >= 2.0 && age >= 22
  end
  
  # 类方法
  def self.create_cs_student(name, birth_year, student_id)
    new(name, birth_year, student_id, "计算机科学")
  end
end

# 多重继承替代方案 - 模块混入演示
module Teachable
  def teach(subject)
    puts "#{@name}正在教授#{subject}"
  end
  
  def assign_homework(assignment)
    puts "#{@name}布置了作业：#{assignment}"
  end
end

module Researchable
  def conduct_research(topic)
    puts "#{@name}正在研究#{topic}"
  end
  
  def publish_paper(title)
    puts "#{@name}发表了论文：《#{title}》"
  end
end

# Teacher类 - 继承Person并混入模块
class Teacher < Person
  include Teachable
  include Researchable
  
  attr_accessor :department, :salary, :courses
  
  def initialize(name, birth_year, department, email = nil)
    super(name, birth_year, email)
    @department = department
    @courses = []
    
    puts "创建了新的Teacher: #{@name}，部门: #{@department}".colorize(:magenta)
  end
  
  def introduce
    super + "，我是#{@department}的老师"
  end
  
  def add_course(course)
    @courses << course
    puts "#{@name}添加了课程：#{course}"
  end
end

# 访问控制演示类
class AccessControlDemo
  def initialize
    @public_var = "公开变量"
    @private_var = "私有变量"
    @protected_var = "受保护变量"
  end
  
  # 公开方法
  def public_method
    puts "这是公开方法，可以被任何地方调用"
    puts "可以访问: #{@public_var}"
    
    # 在类内部可以调用私有和受保护方法
    private_method
    protected_method
  end
  
  # 私有方法
  private
  
  def private_method
    puts "这是私有方法，只能在类内部调用"
    puts "可以访问: #{@private_var}"
  end
  
  # 受保护方法
  protected
  
  def protected_method
    puts "这是受保护方法，可以被同类和子类调用"
    puts "可以访问: #{@protected_var}"
  end
  
  def compare_with(other)
    # 受保护方法可以在同类实例间调用
    puts "比较两个实例的受保护变量："
    puts "自己的: #{@protected_var}"
    puts "对方的: #{other.send(:protected_method)}"
  end
end

# OOP演示主类
class OOPDemo
  def self.run_basic_demo
    puts "=== Ruby基础OOP演示 ===\n".colorize(:blue)
    
    # 创建对象
    puts "1. 创建对象:".colorize(:yellow)
    person1 = Person.new("张三", 1990, "zhangsan@example.com")
    person2 = Person.new("李四", 1985)
    
    puts "\n2. 使用对象方法:".colorize(:yellow)
    puts person1.introduce.colorize(:green)
    puts "#{person1.name}是否成年: #{person1.adult?}".colorize(:green)
    
    puts "\n3. 访问器方法:".colorize(:yellow)
    puts "邮箱: #{person1.email}".colorize(:green)
    person1.phone = "123-456-7890"
    puts "电话: #{person1.phone}".colorize(:green)
    
    puts "\n4. 类方法和类变量:".colorize(:yellow)
    puts "总人口: #{Person.population}".colorize(:green)
    puts "物种: #{Person::SPECIES}".colorize(:green)
    
    anonymous = Person.create_anonymous
    puts "匿名用户: #{anonymous.introduce}".colorize(:green)
    puts "更新后的总人口: #{Person.population}".colorize(:green)
  end
  
  def self.run_inheritance_demo
    puts "\n=== Ruby继承演示 ===\n".colorize(:blue)
    
    puts "1. 创建子类对象:".colorize(:yellow)
    student = Student.new("王五", 2000, "S001", "计算机科学", "wangwu@university.edu")
    
    puts "\n2. 方法重写:".colorize(:yellow)
    puts student.introduce.colorize(:green)
    
    puts "\n3. 子类特有方法:".colorize(:yellow)
    student.study("Ruby编程")
    student.gpa = 3.5
    puts "#{student.name}是否能毕业: #{student.graduate?}".colorize(:green)
    
    puts "\n4. 继承链检查:".colorize(:yellow)
    puts "student是Student的实例: #{student.is_a?(Student)}".colorize(:green)
    puts "student是Person的实例: #{student.is_a?(Person)}".colorize(:green)
    puts "Student的父类: #{Student.superclass}".colorize(:green)
    
    puts "\n5. 类方法继承:".colorize(:yellow)
    cs_student = Student.create_cs_student("赵六", 1999, "S002")
    puts cs_student.introduce.colorize(:green)
  end
  
  def self.run_mixin_demo
    puts "\n=== Ruby模块混入演示 ===\n".colorize(:blue)
    
    puts "1. 创建Teacher对象:".colorize(:yellow)
    teacher = Teacher.new("刘教授", 1975, "计算机系", "liu@university.edu")
    
    puts "\n2. 使用混入的方法:".colorize(:yellow)
    teacher.teach("面向对象编程")
    teacher.assign_homework("实现一个简单的计算器")
    teacher.conduct_research("人工智能算法")
    teacher.publish_paper("基于深度学习的图像识别技术研究")
    
    puts "\n3. 检查模块包含关系:".colorize(:yellow)
    puts "Teacher包含Teachable: #{Teacher.include?(Teachable)}".colorize(:green)
    puts "Teacher包含Researchable: #{Teacher.include?(Researchable)}".colorize(:green)
    
    puts "\n4. 方法查找链:".colorize(:yellow)
    puts "Teacher的祖先链: #{Teacher.ancestors}".colorize(:green)
  end
  
  def self.run_access_control_demo
    puts "\n=== Ruby访问控制演示 ===\n".colorize(:blue)
    
    demo1 = AccessControlDemo.new
    demo2 = AccessControlDemo.new
    
    puts "1. 调用公开方法:".colorize(:yellow)
    demo1.public_method
    
    puts "\n2. 尝试调用私有方法:".colorize(:yellow)
    begin
      demo1.private_method
    rescue NoMethodError => e
      puts "错误: #{e.message}".colorize(:red)
    end
    
    puts "\n3. 通过send调用私有方法:".colorize(:yellow)
    demo1.send(:private_method)
    
    puts "\n4. 同类实例间的受保护方法调用:".colorize(:yellow)
    demo1.compare_with(demo2)
  end
  
  def self.run_advanced_demo
    puts "\n=== Ruby高级OOP特性演示 ===\n".colorize(:blue)
    
    # 动态方法定义
    puts "1. 动态方法定义:".colorize(:yellow)
    class DynamicClass
      ['red', 'green', 'blue'].each do |color|
        define_method("set_#{color}") do |value|
          instance_variable_set("@#{color}", value)
          puts "设置#{color}为#{value}"
        end
        
        define_method("get_#{color}") do
          instance_variable_get("@#{color}")
        end
      end
    end
    
    obj = DynamicClass.new
    obj.set_red(255)
    obj.set_green(128)
    puts "红色值: #{obj.get_red}".colorize(:green)
    
    # 方法别名
    puts "\n2. 方法别名:".colorize(:yellow)
    class Person
      alias_method :full_name, :name
      alias :get_age :age
    end
    
    person = Person.new("测试用户", 1990)
    puts "全名: #{person.full_name}".colorize(:green)
    puts "年龄: #{person.get_age}".colorize(:green)
    
    # 单例方法
    puts "\n3. 单例方法:".colorize(:yellow)
    special_person = Person.new("特殊用户", 1990)
    
    def special_person.special_ability
      "我有特殊能力！"
    end
    
    puts special_person.special_ability.colorize(:green)
    
    # 类的单例方法
    puts "\n4. 类的单例方法:".colorize(:yellow)
    class << Person
      def motto
        "活到老，学到老"
      end
    end
    
    puts "Person类的座右铭: #{Person.motto}".colorize(:green)
  end
  
  def self.run_all_demos
    run_basic_demo
    run_inheritance_demo
    run_mixin_demo
    run_access_control_demo
    run_advanced_demo
  end
end