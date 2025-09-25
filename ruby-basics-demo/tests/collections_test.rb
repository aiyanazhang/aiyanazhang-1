# 集合操作模块测试

require_relative 'test_helper'
require 'collections/array_demo'
require 'collections/hash_demo'
require 'collections/collections_utils'

class CollectionsTest < RubyBasicsTest
  def setup
    super
    @array_demo = ArrayDemo.new
    @hash_demo = HashDemo.new
  end
  
  def test_array_demo_creation
    assert_instance_of ArrayDemo, @array_demo
    refute_nil @array_demo
  end
  
  def test_array_demo_methods_exist
    assert_respond_to @array_demo, :demonstrate_array_creation
    assert_respond_to @array_demo, :demonstrate_array_access
    assert_respond_to @array_demo, :demonstrate_array_modification
    assert_respond_to @array_demo, :demonstrate_array_search_filter
    assert_respond_to @array_demo, :demonstrate_array_transformation
    assert_respond_to @array_demo, :demonstrate_advanced_features
    assert_respond_to @array_demo, :run_all_demos
  end
  
  def test_array_creation_demonstration
    assert_output_includes "=== Ruby数组创建演示 ===" do
      @array_demo.demonstrate_array_creation
    end
  end
  
  def test_array_access_demonstration
    assert_output_includes "=== Ruby数组访问和修改演示 ===" do
      @array_demo.demonstrate_array_access
    end
  end
  
  def test_array_modification_demonstration
    assert_output_includes "=== Ruby数组添加和删除演示 ===" do
      @array_demo.demonstrate_array_modification
    end
  end
  
  def test_array_search_filter_demonstration
    assert_output_includes "=== Ruby数组查找和过滤演示 ===" do
      @array_demo.demonstrate_array_search_filter
    end
  end
  
  def test_array_transformation_demonstration
    assert_output_includes "=== Ruby数组变换演示 ===" do
      @array_demo.demonstrate_array_transformation
    end
  end
  
  def test_array_advanced_features_demonstration
    assert_output_includes "=== Ruby数组高级特性演示 ===" do
      @array_demo.demonstrate_advanced_features
    end
  end
  
  def test_hash_demo_creation
    assert_instance_of HashDemo, @hash_demo
    refute_nil @hash_demo
  end
  
  def test_hash_demo_methods_exist
    assert_respond_to @hash_demo, :demonstrate_hash_creation
    assert_respond_to @hash_demo, :demonstrate_hash_access
    assert_respond_to @hash_demo, :demonstrate_hash_modification
    assert_respond_to @hash_demo, :demonstrate_hash_iteration
    assert_respond_to @hash_demo, :demonstrate_hash_search_filter
    assert_respond_to @hash_demo, :demonstrate_hash_merge_conversion
    assert_respond_to @hash_demo, :demonstrate_advanced_features
    assert_respond_to @hash_demo, :run_all_demos
  end
  
  def test_hash_creation_demonstration
    assert_output_includes "=== Ruby哈希创建演示 ===" do
      @hash_demo.demonstrate_hash_creation
    end
  end
  
  def test_hash_access_demonstration
    assert_output_includes "=== Ruby哈希访问和修改演示 ===" do
      @hash_demo.demonstrate_hash_access
    end
  end
  
  def test_collections_utils_methods
    assert_respond_to CollectionsUtils, :run_interactive_demo
    assert_respond_to CollectionsUtils, :demonstrate_conversions
    assert_respond_to CollectionsUtils, :demonstrate_practical_examples
  end
  
  def test_collections_utils_demo
    assert_output_includes "=== Ruby集合综合演示 ===" do
      CollectionsUtils.run_interactive_demo
    end
  end
  
  def test_conversions_demonstration
    assert_output_includes "=== 集合转换演示 ===" do
      CollectionsUtils.demonstrate_conversions
    end
  end
  
  def test_practical_examples_demonstration
    assert_output_includes "=== 实际应用示例 ===" do
      CollectionsUtils.demonstrate_practical_examples
    end
  end
  
  # 测试实际的Ruby集合概念
  def test_array_operations
    # 数组创建
    arr = [1, 2, 3, 4, 5]
    assert_equal 5, arr.length
    assert_equal 1, arr.first
    assert_equal 5, arr.last
    
    # 数组访问
    assert_equal 3, arr[2]
    assert_equal 5, arr[-1]
    
    # 数组修改
    arr.push(6)
    assert_equal 6, arr.length
    assert_equal 6, arr.last
    
    # 数组变换
    doubled = arr.map { |x| x * 2 }
    assert_equal [2, 4, 6, 8, 10, 12], doubled
    
    # 数组过滤
    evens = arr.select { |x| x.even? }
    assert_equal [2, 4, 6], evens
  end
  
  def test_hash_operations
    # 哈希创建
    hash = { name: 'Ruby', version: 3.0 }
    assert_equal 2, hash.size
    assert_equal 'Ruby', hash[:name]
    
    # 哈希修改
    hash[:active] = true
    assert_equal true, hash[:active]
    assert_equal 3, hash.size
    
    # 哈希遍历
    keys = []
    hash.each_key { |key| keys << key }
    assert_includes keys, :name
    assert_includes keys, :version
    assert_includes keys, :active
    
    # 哈希合并
    additional = { language: 'programming' }
    merged = hash.merge(additional)
    assert_equal 4, merged.size
    assert_equal 'programming', merged[:language]
  end
  
  def test_collection_conversions
    # 数组转哈希
    pairs = [[:a, 1], [:b, 2], [:c, 3]]
    hash = Hash[pairs]
    assert_equal({ a: 1, b: 2, c: 3 }, hash)
    
    # 哈希转数组
    arr = hash.to_a
    assert_instance_of Array, arr
    assert_equal 3, arr.length
    
    # 范围转数组
    range_arr = (1..5).to_a
    assert_equal [1, 2, 3, 4, 5], range_arr
  end
  
  def test_run_all_demos
    assert_no_errors do
      @array_demo.run_all_demos
    end
    
    assert_no_errors do
      @hash_demo.run_all_demos
    end
  end
end