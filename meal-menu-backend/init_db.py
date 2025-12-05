import json
from models import init_database, add_dish

def load_preset_dishes():
    init_database()
    
    with open('data/preset_dishes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("正在导入预设菜品...")
    
    for dish in data['dishes']:
        add_dish(dish['name'], dish['category'], is_preset=1)
        print(f"已添加菜品: {dish['name']}")
    
    for soup in data['soups']:
        add_dish(soup['name'], soup['category'], is_preset=1)
        print(f"已添加汤: {soup['name']}")
    
    print(f"\n完成! 共导入 {len(data['dishes'])} 道菜和 {len(data['soups'])} 种汤")

if __name__ == '__main__':
    load_preset_dishes()
